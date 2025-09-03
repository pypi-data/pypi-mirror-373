# Copyright © Nexa AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.s

from __future__ import annotations

import os
import json
import mlx.core as mx
import mlx.nn as nn
import numpy as np
import time
from pathlib import Path
from typing import Any, List, Optional, Sequence
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Import necessary modules 
from transformers import AutoTokenizer

# Import from ml.py for API alignment (assuming similar structure)
try:
    from ml import (
        Reranker as BaseReranker,
        Path as PathType,
    )
except ImportError:
    # Fallback to local definitions if ml.py not available
    PathType = Path
    BaseReranker = ABC

# Import profiling module
from profiling import ProfilingMixin, ProfilingData, StopReason

# Import the model implementation
from .modeling.nexa_jina_rerank import Model, ModelArgs


@dataclass
class RerankConfig:
    """Configuration for reranking."""
    batch_size: int = 1
    normalize: bool = True
    normalize_method: str = "softmax"  # "softmax" | "min-max" | "none"

    def __init__(
        self,
        batch_size: int = 1,
        normalize: bool = True,
        normalize_method: str = "softmax",
    ) -> None:
        self.batch_size = batch_size
        self.normalize = normalize
        self.normalize_method = normalize_method


class Reranker(BaseReranker, ProfilingMixin):
    """
    Reranker interface for MLX reranking models.
    API aligned with ml.py Reranker abstract base class.
    """

    def __init__(
        self,
        model_path: PathType,
        tokenizer_path: PathType,
        device: Optional[str] = None,
    ) -> None:
        """Initialize the Reranker model."""
        # Initialize profiling mixin
        ProfilingMixin.__init__(self)

        # Store paths
        if (os.path.isfile(model_path)):
            model_path = os.path.dirname(model_path)
            
        # Call parent constructor if inheriting from ml.py
        if hasattr(super(), '__init__'):
            super().__init__(model_path, tokenizer_path, device)
        
        # Store paths and device
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.device = device if device is not None else "cpu"
        
        # Initialize model and tokenizer as None
        self.model = None
        self.tokenizer = None
        self.config = None

    def destroy(self) -> None:
        """Destroy the model and free resources."""
        self.model = None
        self.tokenizer = None
        self.config = None

    def load_model(self, model_path: PathType, extra_data: Any = None) -> bool:
        """Load model from path."""
        try:
            # Use the provided model_path or fall back to instance path
            if model_path:
                # Apply same file-to-directory conversion as in __init__
                if os.path.isfile(model_path):
                    model_path = os.path.dirname(model_path)
                self.model_path = model_path
            
            # Load the model using internal implementation
            self.model = self._load_jina_model(self.model_path)
            self.tokenizer = self._load_tokenizer()
            
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def close(self) -> None:
        """Close the model."""
        self.destroy()

    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        config: Optional[RerankConfig] = None,
        clear_cache: bool = True,
    ) -> mx.array:
        """Rerank documents given a query."""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if config is None:
            config = RerankConfig()
        
        # Start profiling
        self._start_profiling()
        self._prompt_start()
        
        all_scores = []
        
        # Process documents in batches
        batch_size = config.batch_size
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_scores = self._rerank_batch(query, batch_docs, config)
            all_scores.append(batch_scores)
        
        if clear_cache:
            mx.clear_cache()
        
        # End prompt processing, start decode
        self._prompt_end()
        self._decode_start()
        
        # Concatenate all batch scores into a single array
        res = mx.concatenate(all_scores, axis=0) if len(all_scores) > 1 else all_scores[0]
        
        # End decode and profiling
        self._decode_end()
        self._set_stop_reason(StopReason.ML_STOP_REASON_COMPLETED)
        self._end_profiling()
        
        return res

    def _load_jina_model(self, model_dir: str) -> Model:
        """Initialize and load the Jina V2 rerank model."""
        
        # Validate that model path exists
        if not os.path.exists(model_dir):
            raise ValueError(f"Model path does not exist: {model_dir}")
            
        # Store model directory for tokenizer loading
        self._model_dir = model_dir

        # Create model config
        config = ModelArgs()
        model = Model(config)
        
        # Load weights
        weight_file = os.path.join(model_dir, "model.safetensors")
        if not os.path.exists(weight_file):
            # Try alternative naming patterns
            safetensors_files = [f for f in os.listdir(model_dir) if f.endswith('.safetensors')]
            if safetensors_files:
                weight_file = os.path.join(model_dir, safetensors_files[0])
            else:
                raise FileNotFoundError(f"No .safetensors file found in {model_dir}")

        model.load_weights(weight_file, strict=True)
        model.eval()
        
        return model

    def _load_tokenizer(self) -> AutoTokenizer:
        """Load and configure the tokenizer."""
        return AutoTokenizer.from_pretrained(self._model_dir)

    def _rerank_batch(self, query: str, documents: List[str], config: RerankConfig) -> mx.array:
        """Rerank a batch of documents and return their scores."""
        # Prepare inputs
        input_ids, attention_mask, token_type_ids, position_ids = self._prepare_inputs(
            query, documents, self.tokenizer, max_length=1024
        )
        
        # Run inference
        scores = self.model.nexa_forward(input_ids, attention_mask, token_type_ids, position_ids)
        scores = mx.squeeze(scores, axis=-1)
        
        # Apply normalization if requested
        if config.normalize:
            scores = self._normalize_scores(scores, config.normalize_method)
        
        return scores

    def _create_position_ids_from_input_ids(self, input_ids, padding_idx, past_key_values_length=0):
        """Create position ids from input ids, accounting for padding tokens"""
        mask = (input_ids != padding_idx).astype(mx.int32)
        incremental_indices = (mx.cumsum(mask, axis=1) + past_key_values_length) * mask
        return incremental_indices.astype(mx.int32) + padding_idx

    def _prepare_inputs(self, query, documents, tokenizer, max_length=1024):
        """Prepare inputs for the model - match torch exactly"""
        sentence_pairs = [[query, doc] for doc in documents]
        inputs = tokenizer(
            sentence_pairs,
            padding="max_length",
            truncation=True,
            return_tensors="np",
            max_length=max_length,
        )

        input_ids = mx.array(inputs["input_ids"]).astype(mx.int32)
        seqlen = input_ids.shape[1]
        attention_mask = mx.array(inputs["attention_mask"]).astype(mx.float32)

        # Create token_type_ids as 1D tensor like torch, then broadcast for each batch item
        token_type_ids_1d = mx.zeros(seqlen, dtype=mx.int32)
        batch_size = input_ids.shape[0]
        token_type_ids = mx.broadcast_to(
            mx.expand_dims(token_type_ids_1d, axis=0), (batch_size, seqlen)
        )

        # Create position ids for each sequence in the batch
        position_ids = self._create_position_ids_from_input_ids(input_ids, padding_idx=1)

        return input_ids, attention_mask, token_type_ids, position_ids

    def _normalize_scores(self, scores: mx.array, method: str) -> mx.array:
        """Normalize scores using specified method."""
        if method == "none":
            return scores
        elif method == "softmax":
            # For 1D arrays, use axis=0; for higher dims, use axis=-1
            if len(scores.shape) == 1:
                return mx.softmax(scores, axis=0)
            else:
                return mx.softmax(scores, axis=-1)
        elif method == "min-max":
            min_val = mx.min(scores)
            max_val = mx.max(scores)
            if max_val > min_val:
                return (scores - min_val) / (max_val - min_val)
            return scores
        else:
            return scores


# Factory function for creating reranker instances
def create_reranker(
    model_path: PathType,
    tokenizer_path: Optional[PathType] = None,
    device: Optional[str] = None,
) -> Reranker:
    """Create and return a Reranker instance."""
    if tokenizer_path is None:
        tokenizer_path = model_path
    
    return Reranker(model_path, tokenizer_path, device)