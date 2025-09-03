from typing import List, Optional, Union
from abc import abstractmethod
from dataclasses import dataclass

from nexaai.base import BaseModel
from nexaai.common import PluginID


@dataclass
class Image:
    """Image data structure."""
    data: List[float]  # width × height × channels
    width: int
    height: int
    channels: int  # 3 = RGB, 4 = RGBA


@dataclass
class ImageSamplerConfig:
    """Configuration for image sampling."""
    method: str = "ddim"
    steps: int = 20
    guidance_scale: float = 7.5
    eta: float = 0.0
    seed: int = -1  # –1 for random


@dataclass
class ImageGenerationConfig:
    """Configuration for image generation."""
    prompts: Union[str, List[str]]
    negative_prompts: Optional[Union[str, List[str]]] = None
    height: int = 512
    width: int = 512
    sampler_config: Optional[ImageSamplerConfig] = None
    lora_id: int = -1  # –1 for none
    init_image: Optional[Image] = None
    strength: float = 1.0
    n_images: int = 1
    n_rows: int = 1
    decoding_batch_size: int = 1


@dataclass
class SchedulerConfig:
    """Configuration for diffusion scheduler."""
    type: str = "ddim"
    num_train_timesteps: int = 1000
    steps_offset: int = 0  # An offset added to the inference steps
    beta_start: float = 0.00085
    beta_end: float = 0.012
    beta_schedule: str = "scaled_linear"
    prediction_type: str = "epsilon"
    timestep_type: str = "discrete"
    timestep_spacing: str = "linspace"
    interpolation_type: str = "linear"
    config_path: Optional[str] = None


class ImageGen(BaseModel):
    """Abstract base class for image generation models."""

    def __init__(self):
        """Initialize base image generation class."""
        pass

    @classmethod
    def _load_from(cls,
                   model_path: str,
                   scheduler_config_path: str = "",
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None,
                   float16: bool = True,
                   quantize: bool = False
        ) -> 'ImageGen':
        """Load image generation model from local path, routing to appropriate implementation."""
        # Check plugin_id value for routing - handle both enum and string
        plugin_value = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        if plugin_value == "mlx":
            from nexaai.image_gen_impl.mlx_image_gen_impl import MLXImageGenImpl
            return MLXImageGenImpl._load_from(model_path, scheduler_config_path, plugin_id, device_id, float16, quantize)
        else:
            from nexaai.image_gen_impl.pybind_image_gen_impl import PyBindImageGenImpl
            return PyBindImageGenImpl._load_from(model_path, scheduler_config_path, plugin_id, device_id, float16, quantize)

    @abstractmethod
    def load_model(self, model_path: str, extra_data: Optional[str] = None) -> bool:
        """Load model from path."""
        pass

    @abstractmethod
    def set_scheduler(self, config: SchedulerConfig) -> None:
        """Set scheduler configuration."""
        pass

    @abstractmethod
    def set_sampler(self, config: ImageSamplerConfig) -> None:
        """Set sampler configuration."""
        pass

    @abstractmethod
    def reset_sampler(self) -> None:
        """Reset sampler to default configuration."""
        pass

    @abstractmethod
    def txt2img(self, prompt: str, config: ImageGenerationConfig) -> Image:
        """Generate image from text prompt."""
        pass

    @abstractmethod
    def img2img(self, init_image: Image, prompt: str, config: ImageGenerationConfig) -> Image:
        """Generate image from initial image and text prompt."""
        pass

    @abstractmethod
    def generate(self, config: ImageGenerationConfig) -> Image:
        """Generate image from configuration."""
        pass

    @abstractmethod
    def set_lora(self, lora_id: int) -> None:
        """Set active LoRA adapter."""
        pass

    @abstractmethod
    def add_lora(self, lora_path: str) -> int:
        """Add LoRA adapter and return its ID."""
        pass

    @abstractmethod
    def remove_lora(self, lora_id: int) -> None:
        """Remove LoRA adapter."""
        pass

    @abstractmethod
    def list_loras(self) -> List[int]:
        """List available LoRA adapters."""
        pass
