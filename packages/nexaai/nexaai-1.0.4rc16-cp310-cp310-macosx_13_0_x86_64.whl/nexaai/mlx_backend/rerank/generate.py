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
# limitations under the License.

import sys
import os
import mlx.core as mx
import mlx.nn as nn
import numpy as np
import time

from transformers import AutoTokenizer
from huggingface_hub import snapshot_download
from .modeling.nexa_jina_rerank import Model, ModelArgs


def create_position_ids_from_input_ids(input_ids, padding_idx, past_key_values_length=0):
    """Create position ids from input ids, accounting for padding tokens"""
    mask = (input_ids != padding_idx).astype(mx.int32)
    incremental_indices = (mx.cumsum(mask, axis=1) + past_key_values_length) * mask
    return incremental_indices.astype(mx.int32) + padding_idx


def prepare_inputs(query, documents, tokenizer, max_length=1024):
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
    position_ids = create_position_ids_from_input_ids(input_ids, padding_idx=1)

    return input_ids, attention_mask, token_type_ids, position_ids


def load_model(model_id):
    """Initialize and load the Jina V2 rerank model."""
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = f"{curr_dir}/modelfiles/nexaml_jina_v2_rerank_mlx"
    
    # Download model if not exists
    if not os.path.exists(model_dir):
        print(f"Downloading model {model_id}...")
        
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            snapshot_download(
                repo_id=model_id,
                allow_patterns=["*.safetensors", "config.json", "tokenizer*"],
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            print("Model download completed!")
        except Exception as e:
            print(f"Failed to download model: {e}")
            print("Try: huggingface-cli login (if authentication required)")
            raise

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

    print(f"Loading weights from: {weight_file}")
    model.load_weights(weight_file, strict=True)
    model.eval()
    
    return model, model_dir


def load_tokenizer(model_path):
    """Load and configure the tokenizer."""
    return AutoTokenizer.from_pretrained(model_path)


def rerank_documents(model, tokenizer, query, documents, max_length=1024):
    """Rerank documents based on query relevance."""
    # Prepare inputs
    input_ids, attention_mask, token_type_ids, position_ids = prepare_inputs(
        query, documents, tokenizer, max_length
    )
    
    # Run inference
    start_time = time.time()
    scores = model.nexa_forward(input_ids, attention_mask, token_type_ids, position_ids)
    scores = mx.squeeze(scores, axis=-1)
    end_time = time.time()
    
    # Apply sigmoid to get probabilities
    scores_sigmoid = mx.sigmoid(scores)
    
    inference_time = (end_time - start_time) * 1000  # Convert to ms
    
    return scores, scores_sigmoid, inference_time


def main(model_id):
    """Main function to handle reranking demonstration."""
    
    # Load model and tokenizer
    model, model_path = load_model(model_id)
    tokenizer = load_tokenizer(model_path)
    
    # Example query and documents
    query = "What are the health benefits of green tea?"
    documents = [
        "Green tea is rich in antioxidants and may improve brain function.",
        "Coffee contains caffeine and can boost energy levels.",
        "Das Trinken von grünem Tee kann das Risiko für Herzkrankheiten senken.",
        "Black tea is another popular beverage with its own health benefits.",
    ]
    
    # Perform reranking
    scores, scores_sigmoid, inference_time = rerank_documents(
        model, tokenizer, query, documents
    )
    
    # Display results
    print("=" * 70)
    print("Reranking Results:")
    print("=" * 70)
    print(f"Query: {query}")
    print()
    
    for i, (doc, score, prob) in enumerate(zip(documents, scores.tolist(), scores_sigmoid.tolist())):
        print(f"Document {i+1}:")
        print(f"  Text: {doc}")
        print(f"  Score: {score:.4f}")
        print(f"  Probability: {prob:.4f}")
        print()
    
    print(f"Inference time: {inference_time:.1f}ms")
    print(f"Throughput: {len(documents)/inference_time*1000:.1f} docs/s")


if __name__ == "__main__":
    model_id = "nexaml/jina-v2-rerank-mlx"
    main(model_id)