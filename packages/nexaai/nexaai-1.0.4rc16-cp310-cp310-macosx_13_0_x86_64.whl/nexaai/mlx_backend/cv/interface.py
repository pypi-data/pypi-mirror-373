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

from __future__ import annotations

import os
import json
import time
import cv2
import numpy as np
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Union
from PIL import Image
from dataclasses import dataclass

# Import necessary modules 
import mlx.core as mx

# Import from ml.py for API alignment
from ml import (
    CVModel as BaseCVModel,
    CVModelConfig,
    CVResults,
    CVResult,
    CVCapabilities,
    Path as PathType,
)

# Import the model implementation
from .modeling.pp_ocr_v4 import Config, TextSystem

@dataclass
class CVConfig:
    """Configuration for CV processing."""
    batch_size: int = 1
    drop_score: float = 0.5
    font_path: Optional[str] = None

    def __init__(
        self,
        batch_size: int = 1,
        drop_score: float = 0.5,
        font_path: Optional[str] = None,
    ) -> None:
        self.batch_size = batch_size
        self.drop_score = drop_score
        self.font_path = font_path


class CVModel(BaseCVModel):
    """
    CV Model interface for MLX OCR models.
    API aligned with ml.py CVModel abstract base class.
    """
    def __init__(
        self,
        config: CVModelConfig,
        device: Optional[str] = None,
    ) -> None:
        super().__init__(config, device)
        # print(f"config: {config}")
        # TODO: this hack is to support local model path
        # hack only support pp_ocr_v4
        rec_model_path_str = str(config.rec_model_path) if config.rec_model_path else None
        model_cache_dir = os.path.dirname(rec_model_path_str) if rec_model_path_str else None
        # print(f"model_cache_dir: {model_cache_dir}")
        cfg = Config(model_cache_dir)
        # print(f"cfg: {cfg}")
        cfg.device = self.device
        self.ocr_system = TextSystem(cfg)

    def destroy(self) -> None:
        """Destroy the model and free resources."""
        self.ocr_system = None
        self.config = None

    def close(self) -> None:
        """Close the model."""
        self.destroy()

    def infer(self, input_image_path: str, clear_cache: bool = True) -> CVResults:
        """Perform inference on image."""
        if self.ocr_system is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Load image
        img = self._load_image(input_image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {input_image_path}")
        
        # Process with OCR
        boxes, recs = self.ocr_system(img)

        if clear_cache:
            mx.clear_cache()
        
        # Convert to CVResults format
        results = []
        for box, (text, score) in zip(boxes, recs):
            # Create CVResult
            result = CVResult(
                text=text,
                confidence=score,
                # Note: OCR doesn't use bounding boxes in the same way as detection models
                # but we can store the box coordinates if needed
            )
            results.append(result)
        
        return CVResults(results=results, result_count=len(results))

    
    def _load_image(self, image_path: Union[str, PathType]) -> Optional[np.ndarray]:
        """Load image from path."""
        try:
            # Check if it's a GIF
            if str(image_path).lower().endswith('.gif'):
                gif = cv2.VideoCapture(str(image_path))
                ret, frame = gif.read()
                if not ret:
                    return None
                if len(frame.shape) == 2 or frame.shape[-1] == 1:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                return frame[:, :, ::-1]  # BGR to RGB
            else:
                img = cv2.imread(str(image_path))
                if img is None:
                    return None
                return img
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None



def create_cv_model(
    config: CVModelConfig,
    device: Optional[str] = None,
) -> CVModel:
    """Create a CV model instance."""
    return CVModel(config, device) 