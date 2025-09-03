from typing import List, Optional, Union
from abc import abstractmethod
from dataclasses import dataclass

from nexaai.base import BaseModel
from nexaai.common import PluginID


@dataclass
class BoundingBox:
    """Generic bounding box structure."""
    x: float  # X coordinate (normalized or pixel, depends on model)
    y: float  # Y coordinate (normalized or pixel, depends on model) 
    width: float  # Width
    height: float  # Height


@dataclass
class CVResult:
    """Generic detection/classification result."""
    image_paths: Optional[List[str]] = None  # Output image paths
    image_count: int = 0  # Number of output images
    class_id: int = 0  # Class ID (example: ConvNext)
    confidence: float = 0.0  # Confidence score [0.0-1.0]
    bbox: Optional[BoundingBox] = None  # Bounding box (example: YOLO)
    text: Optional[str] = None  # Text result (example: OCR)
    embedding: Optional[List[float]] = None  # Feature embedding (example: CLIP embedding)
    embedding_dim: int = 0  # Embedding dimension


@dataclass
class CVResults:
    """Generic CV inference result."""
    results: List[CVResult]  # Array of CV results
    result_count: int  # Number of CV results


class CVCapabilities:
    """CV capabilities enum."""
    OCR = 0  # OCR
    CLASSIFICATION = 1  # Classification
    SEGMENTATION = 2  # Segmentation
    CUSTOM = 3  # Custom task


@dataclass
class CVModelConfig:
    """CV model preprocessing configuration."""
    capabilities: int  # CVCapabilities

    # MLX-OCR
    det_model_path: Optional[str] = None  # Detection model path
    rec_model_path: Optional[str] = None  # Recognition model path

    # QNN
    model_path: Optional[str] = None  # Model path
    system_library_path: Optional[str] = None  # System library path
    backend_library_path: Optional[str] = None  # Backend library path
    extension_library_path: Optional[str] = None  # Extension library path
    config_file_path: Optional[str] = None  # Config file path
    char_dict_path: Optional[str] = None  # Character dictionary path


class CVModel(BaseModel):
    """Abstract base class for generic computer vision models."""

    def __init__(self):
        """Initialize base CV model class."""
        pass

    @classmethod
    def _load_from(cls,
                   _: str,  # TODO: remove this argument, this is a hack to make api design happy
                   config: CVModelConfig,
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None
        ) -> 'CVModel':
        """Load CV model from configuration, routing to appropriate implementation."""
        # Check plugin_id value for routing - handle both enum and string
        plugin_value = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        if plugin_value == "mlx":
            from nexaai.cv_impl.mlx_cv_impl import MLXCVImpl
            return MLXCVImpl._load_from(config, plugin_id, device_id)
        else:
            from nexaai.cv_impl.pybind_cv_impl import PyBindCVImpl
            return PyBindCVImpl._load_from(config, plugin_id, device_id)

    @abstractmethod
    def infer(self, input_image_path: str) -> CVResults:
        """Perform inference on image."""
        pass
