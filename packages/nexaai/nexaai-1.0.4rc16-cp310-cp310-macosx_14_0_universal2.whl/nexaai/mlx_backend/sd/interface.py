from __future__ import annotations

import time
from typing import (
    Any,
    Callable,
    List,
    Optional,
)

import mlx.core as mx
import numpy as np
from PIL import Image as PILImage
import mlx.nn as nn
import os

from .modeling import StableDiffusion, StableDiffusionXL

# --------------------------------------------------------------------------------------
# Core aliases & callback protocols
# --------------------------------------------------------------------------------------

Path = str
LogCallback = Callable[[str], None]

# --------------------------------------------------------------------------------------
# Core module functions
# --------------------------------------------------------------------------------------

def init() -> None: 
    """Initialize the stable diffusion module"""
    pass

def deinit() -> None: 
    """Deinitialize the stable diffusion module"""
    pass

def set_log(callback: LogCallback) -> None: 
    """Set the logging callback"""
    pass

def log(message: str) -> None: 
    """Log a message"""
    print(message)

# --------------------------------------------------------------------------------------
# Basic data structures
# --------------------------------------------------------------------------------------

class Image:
    def __init__(self, data: List[float], width: int, height: int, channels: int) -> None:
        """Initialize an image with pixel data"""
        self.data = data
        self.width = width
        self.height = height
        self.channels = channels

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> 'Image':
        """Create Image from numpy array (H, W, C)"""
        height, width, channels = array.shape
        data = array.flatten().tolist()
        return cls(data, width, height, channels)
    
    @classmethod
    def from_pil(cls, pil_image: PILImage.Image) -> 'Image':
        """Create Image from PIL Image"""
        array = np.array(pil_image).astype(np.float32) / 255.0
        return cls.from_numpy(array)
    
    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array (H, W, C)"""
        return np.array(self.data).reshape(self.height, self.width, self.channels)
    
    def to_pil(self) -> PILImage.Image:
        """Convert to PIL Image"""
        array = (self.to_numpy() * 255).astype(np.uint8)
        return PILImage.fromarray(array)

class ImageSamplerConfig:
    def __init__(
        self,
        method: str = "ddim",
        steps: int = 20,
        guidance_scale: float = 7.5,
        eta: float = 0.0,
        seed: int = -1,
    ) -> None:
        """Initialize sampler configuration"""
        self.method = method
        self.steps = steps
        self.guidance_scale = guidance_scale
        self.eta = eta
        self.seed = seed

class ImageGenerationConfig:
    def __init__(
        self,
        prompts: str | List[str],
        negative_prompts: str | List[str] | None = None,
        height: int = 512,
        width: int = 512,
        sampler_config: Optional[ImageSamplerConfig] = None,
        lora_id: int = -1,  # Not used but kept for compatibility
        init_image: Optional[Image] = None,
        strength: float = 1.0,
        n_images: int = 1,
        n_rows: int = 1,
        decoding_batch_size: int = 1,
    ) -> None:
        """Initialize image generation configuration"""
        self.prompts = prompts
        self.negative_prompts = negative_prompts or ""
        self.height = height
        self.width = width
        self.sampler_config = sampler_config or ImageSamplerConfig()
        self.lora_id = lora_id
        self.init_image = init_image
        self.strength = strength
        self.n_images = n_images
        self.n_rows = n_rows
        self.decoding_batch_size = decoding_batch_size

# --------------------------------------------------------------------------------------
# Helper functions - following txt2img.py pattern
# --------------------------------------------------------------------------------------

def load_model(model_path: Path, float16: bool = True, quantize: bool = False) -> StableDiffusion:
    """Load a model from the given path - following txt2img.py pattern"""
    
    # Check if it's a local path or HuggingFace repo
    # If it contains path separators or exists as a file/directory, treat as local
    is_local_path = ('/' in model_path or '\\' in model_path or os.path.exists(model_path))
    
    if is_local_path:
        # For local paths, determine model type from the path or model files
        if "xl" in model_path.lower() or "turbo" in model_path.lower():
            model = StableDiffusionXL(model_path, float16=float16)
        else:
            model = StableDiffusion(model_path, float16=float16)
    else:
        # For HuggingFace repo names, use the original logic
        if "xl" in model_path.lower() or "turbo" in model_path.lower():
            model = StableDiffusionXL(model_path, float16=float16)
        else:
            model = StableDiffusion(model_path, float16=float16)
    
    # Apply quantization if requested - same as txt2img.py
    if quantize:
        if "xl" in model_path.lower() or "turbo" in model_path.lower():
            nn.quantize(
                model.text_encoder_1, class_predicate=lambda _, m: isinstance(m, nn.Linear)
            )
            nn.quantize(
                model.text_encoder_2, class_predicate=lambda _, m: isinstance(m, nn.Linear)
            )
        else:
            nn.quantize(
                model.text_encoder, class_predicate=lambda _, m: isinstance(m, nn.Linear)
            )
        nn.quantize(model.unet, group_size=32, bits=8)
    
    return model

def _prepare_image_for_sd(image: Image, target_width: int, target_height: int) -> mx.array:
    """Prepare image for stable diffusion processing - simplified"""
    # Convert to PIL and resize
    pil_img = image.to_pil()
    pil_img = pil_img.resize((target_width, target_height), PILImage.LANCZOS)
    
    # Convert to array and normalize to [0,1] range (following txt2img.py pattern)
    img_array = np.array(pil_img).astype(np.float32)[:, :, :3]  # Ensure RGB
    img_tensor = mx.array(img_array / 255.0)
    
    return img_tensor

# --------------------------------------------------------------------------------------
# Image generation
# --------------------------------------------------------------------------------------

class ImageGen:
    def __init__(
        self,
        model_path: Path,
        scheduler_config_path: Path = "",  # Make optional
        device: Optional[str] = None,
        float16: bool = True,
        quantize: bool = False,
    ) -> None:
        """Initialize the image generation model"""
        self.model_path = model_path
        self.scheduler_config_path = scheduler_config_path  # Store for compatibility
        self.float16 = float16
        self.quantize = quantize
        self.model = None
    
    def destroy(self) -> None:
        """Clean up resources"""
        self.model = None
    
    def load_model(self, model_path: Path, extra_data: Any = None) -> bool:
        """Load the model from a file"""
        try:
            if os.path.isfile(model_path):
                model_path = os.path.dirname(model_path)
            
            self.model_path = model_path
            self.model = load_model(model_path, self.float16, self.quantize)
            self.model.ensure_models_are_loaded()
            return True
        except Exception as e:
            log(f"Failed to load model: {e}")
            return False
    
    def close(self) -> None:
        """Close the model"""
        self.destroy()
    
    def set_scheduler(self, config: Any) -> None:
        """Set scheduler configuration (placeholder for compatibility)"""
        log("Warning: set_scheduler not implemented")
        pass
    
    def set_sampler(self, config: ImageSamplerConfig) -> None:
        """Set sampler configuration (placeholder for compatibility)"""
        log("Warning: set_sampler not implemented")
        pass
    
    def reset_sampler(self) -> None:
        """Reset sampler configuration (placeholder for compatibility)"""
        log("Warning: reset_sampler not implemented")
        pass
    
    def set_lora(self, lora_id: int) -> None:
        """Set LoRA (placeholder for compatibility)"""
        log("Warning: LoRA management not implemented")
        pass
    
    def add_lora(self, lora_path: Path) -> int:
        """Add LoRA (placeholder for compatibility)"""
        log("Warning: LoRA management not implemented")
        return -1
    
    def remove_lora(self, lora_id: int) -> None:
        """Remove LoRA (placeholder for compatibility)"""
        log("Warning: LoRA management not implemented")
        pass
    
    def list_loras(self) -> List[int]:
        """List LoRAs (placeholder for compatibility)"""
        log("Warning: LoRA management not implemented")
        return []
    
    def txt2img(self, prompt: str, config: ImageGenerationConfig, clear_cache: bool = True) -> Image:
        """Generate an image from a text prompt - following txt2img.py pattern"""
        if not self.model and not self.load_model(self.model_path):
            raise RuntimeError("Model not loaded")
        
        sampler_config = config.sampler_config
        
        # Extract prompts
        negative_prompt = ""
        if config.negative_prompts:
            negative_prompt = config.negative_prompts if isinstance(config.negative_prompts, str) else config.negative_prompts[0]
        
        try:
            # Generate latents - following txt2img.py approach
            latents_generator = self.model.generate_latents(
                prompt,
                n_images=1,
                num_steps=sampler_config.steps,
                cfg_weight=sampler_config.guidance_scale,
                negative_text=negative_prompt,
                seed=sampler_config.seed if sampler_config.seed >= 0 else None
            )
            
            # Get final latents - following txt2img.py pattern
            final_latents = None
            for latents in latents_generator:
                final_latents = latents
                mx.eval(final_latents)
            
            if final_latents is None:
                raise RuntimeError("No latents generated")
            
            # Decode to image - following txt2img.py pattern
            decoded_image = self.model.decode(final_latents)
            mx.eval(decoded_image)
            
            # Convert to numpy array - following txt2img.py pattern
            image_array = np.array(decoded_image.squeeze(0))
            
            if clear_cache:
                mx.clear_cache()
            
            return Image.from_numpy(image_array)
            
        except Exception as e:
            log(f"Generation failed: {e}")
            raise e
    
    def img2img(self, init_image: Image, prompt: str, config: ImageGenerationConfig, clear_cache: bool = True) -> Image:
        """Generate an image from an initial image and a text prompt"""
        if not self.model and not self.load_model(self.model_path):
            raise RuntimeError("Model not loaded")
        
        sampler_config = config.sampler_config
        
        # Extract prompts
        negative_prompt = ""
        if config.negative_prompts:
            negative_prompt = config.negative_prompts if isinstance(config.negative_prompts, str) else config.negative_prompts[0]
        
        try:
            # Prepare image for SD processing
            img_tensor = _prepare_image_for_sd(init_image, config.width, config.height)
            
            # Generate latents from image
            latents_generator = self.model.generate_latents_from_image(
                img_tensor,
                prompt,
                n_images=1,
                strength=config.strength,
                num_steps=sampler_config.steps,
                cfg_weight=sampler_config.guidance_scale,
                negative_text=negative_prompt,
                seed=sampler_config.seed if sampler_config.seed >= 0 else None
            )
            
            # Get final latents
            final_latents = None
            for latents in latents_generator:
                final_latents = latents
                mx.eval(final_latents)
            
            if final_latents is None:
                raise RuntimeError("No latents generated")
            
            # Decode to image
            decoded_image = self.model.decode(final_latents)
            mx.eval(decoded_image)
            
            # Convert to numpy array
            image_array = np.array(decoded_image.squeeze(0))
            
            if clear_cache:
                mx.clear_cache()
            
            return Image.from_numpy(image_array)
            
        except Exception as e:
            log(f"Generation failed: {e}")
            raise e
    
    def generate(self, config: ImageGenerationConfig) -> Image:
        """Generate an image from configuration"""
        if config.init_image:
            prompt = config.prompts if isinstance(config.prompts, str) else config.prompts[0]
            return self.img2img(config.init_image, prompt, config)
        else:
            prompt = config.prompts if isinstance(config.prompts, str) else config.prompts[0]
            return self.txt2img(prompt, config)