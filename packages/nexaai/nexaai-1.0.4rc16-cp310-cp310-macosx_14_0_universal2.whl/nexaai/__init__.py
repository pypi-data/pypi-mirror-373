"""
NexaAI Python bindings for NexaSDK C-lib backend.
"""

import sys
import os

# Add mlx_backend to Python path as individual module (only if it exists)
_current_dir = os.path.dirname(os.path.abspath(__file__))
_mlx_backend_path = os.path.join(_current_dir, "mlx_backend")
# Only add to path if the directory exists (it won't on Windows)
if os.path.exists(_mlx_backend_path) and _mlx_backend_path not in sys.path:
    sys.path.insert(0, _mlx_backend_path)

try:
    from ._version import __version__
except ImportError:
    # Fallback for development or when version file hasn't been generated yet
    __version__ = "0.0.1"

# Import common configuration classes first (no external dependencies)
from .common import ModelConfig, GenerationConfig, ChatMessage, SamplerConfig, PluginID

# Create alias for PluginID to be accessible as plugin_id
plugin_id = PluginID

# Import new feature classes (no external dependencies in base classes)
from .llm import LLM
from .embedder import Embedder, EmbeddingConfig
from .vlm import VLM
from .asr import ASR, ASRConfig, ASRResult
from .cv import CVModel, CVModelConfig, CVResult, CVResults, CVCapabilities, BoundingBox
from .rerank import Reranker, RerankConfig
from .image_gen import ImageGen, ImageGenerationConfig, ImageSamplerConfig, SchedulerConfig, Image
from .tts import TTS, TTSConfig, TTSSamplerConfig, TTSResult

# Build __all__ list dynamically
__all__ = [
    "__version__",
    # Common configurations (always available)
    "ModelConfig",
    "GenerationConfig", 
    "ChatMessage",
    "SamplerConfig",
    "EmbeddingConfig",
    "PluginID",
    "plugin_id",

    "LLM",
    "Embedder",
    "VLM",
    "ASR",
    "CVModel",
    "Reranker",
    "ImageGen",
    "TTS",

    "ASRConfig",
    "ASRResult",
    "CVModelConfig",
    "CVResult",
    "CVResults", 
    "CVCapabilities",
    "BoundingBox",
    "RerankConfig",
    "ImageGenerationConfig",
    "ImageSamplerConfig",
    "SchedulerConfig",
    "Image",
    "TTSConfig",
    "TTSSamplerConfig",
    "TTSResult",
]



