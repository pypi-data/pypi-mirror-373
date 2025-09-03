from typing import Any, List, Optional, Sequence
import argparse
import sys
import os

import mlx.core as mx
import numpy as np

from ml import ASR, ASRConfig, ASRResult, Path as MLPath
from mlx_audio.stt.utils import load_model
from mlx_audio.stt.models.whisper.tokenizer import LANGUAGES
from mlx_audio.stt.models.whisper.whisper import Model
import soundfile as sf
import scipy.signal

from profiling import ProfilingMixin, StopReason


class MlxAsr(ASR, ProfilingMixin):
    """MLX Audio implementation of ASR interface."""
    
    def __init__(
        self,
        model_path: MLPath,
        tokenizer_path: Optional[MLPath],
        language: Optional[str],
        device: Optional[str] = None,
    ) -> None:
        # Initialize profiling mixin
        ProfilingMixin.__init__(self)
        
        if os.path.isfile(model_path):
            model_path = os.path.dirname(model_path)
        
        super().__init__(model_path, tokenizer_path, language, device)
        
        # Load model immediately in constructor
        self.model: Model = load_model(model_path)
        self.model_path = model_path
        
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        if self.model is not None:
            del self.model
            self.model = None
            mx.clear_cache()
            
    def close(self) -> None:
        """Close the model."""
        self.destroy()
        
    def transcribe(
        self,
        audio_path: MLPath,
        language: Optional[str] = None,
        config: Optional[ASRConfig] = None,
        clear_cache: bool = True,
    ) -> ASRResult:
        """Transcribe audio file to text."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Start profiling
        self._start_profiling()
        self._decode_start()
        
        try:
            result = self.model.generate(audio_path)
            
            if clear_cache:
                mx.clear_cache()
            
            self._decode_end()
            self._set_stop_reason(StopReason.ML_STOP_REASON_COMPLETED)
            self._end_profiling()
        except Exception as e:
            self._end_profiling()
            raise RuntimeError(f"Failed to transcribe audio file {audio_path}: {e}")
        
        # Extract confidence scores and timestamps
        confidence_scores = []
        timestamps = []
        
        # Handle different result types: Whisper (STTOutput) vs Parakeet (AlignedResult)
        if hasattr(result, 'segments') and result.segments:
            # Whisper STTOutput format
            for segment in result.segments:
                if 'avg_logprob' in segment:
                    # Convert log probability to confidence score (0-1)
                    confidence = max(0.0, min(1.0, np.exp(segment['avg_logprob'])))
                    confidence_scores.append(confidence)
                else:
                    confidence_scores.append(0.5)  # Default confidence
                    
                start_time = segment.get('start', 0.0)
                end_time = segment.get('end', 0.0)
                timestamps.append((start_time, end_time))
        elif hasattr(result, 'sentences') and result.sentences:
            # Parakeet AlignedResult format
            for sentence in result.sentences:
                confidence_scores.append(0.5)  # Default confidence for Parakeet
                timestamps.append((sentence.start, sentence.end))
        else:
            # Single segment case or empty result
            confidence_scores.append(0.5)
            timestamps.append((0.0, 0.0))  # Default timestamps
            
        return ASRResult(
            transcript=result.text,
            confidence_scores=confidence_scores,
            timestamps=timestamps,
            duration_us=self._get_audio_duration_us(audio_path)
        )
        
    def list_supported_languages(self) -> List[str]:
        """List supported languages."""
        return list(LANGUAGES.keys())

    def _get_audio_duration_us(self, audio_path: MLPath) -> int:
        with sf.SoundFile(audio_path) as f:
            duration_us = f.frames / f.samplerate * 1e6
        return int(duration_us)
