from typing import Generator, Optional, List, Dict, Any, Union
from abc import abstractmethod
import queue
import threading
import base64
from pathlib import Path

from nexaai.common import ModelConfig, GenerationConfig, MultiModalMessage, PluginID
from nexaai.base import BaseModel


class VLM(BaseModel):
    def __init__(self, m_cfg: ModelConfig = ModelConfig()):
        """Initialize base VLM class."""
        self._m_cfg = m_cfg
        self._cancel_event = threading.Event()  # New attribute to control cancellation

    @classmethod
    def _load_from(cls,
                   local_path: str,
                   mmproj_path: str,
                   m_cfg: ModelConfig = ModelConfig(),
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None
        ) -> 'VLM':
        """Load VLM model from local path, routing to appropriate implementation.
        
        Args:
            local_path: Path to the main model file
            mmproj_path: Path to the multimodal projection file
            m_cfg: Model configuration
            plugin_id: Plugin identifier
            device_id: Optional device ID (not used in current binding)
            
        Returns:
            VLM instance
        """
        # Check plugin_id value for routing - handle both enum and string
        plugin_value = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        if plugin_value == "mlx":
            from nexaai.vlm_impl.mlx_vlm_impl import MlxVlmImpl
            return MlxVlmImpl._load_from(local_path, mmproj_path, m_cfg, plugin_id, device_id)
        else:
            from nexaai.vlm_impl.pybind_vlm_impl import PyBindVLMImpl
            return PyBindVLMImpl._load_from(local_path, mmproj_path, m_cfg, plugin_id, device_id)

    @abstractmethod
    def eject(self):
        """Release the model from memory."""
        pass

    def cancel_generation(self):
        """Signal to cancel any ongoing stream generation."""
        self._cancel_event.set()

    def reset_cancel(self):
        """Reset the cancel event. Call before starting a new generation if needed."""
        self._cancel_event.clear()

    @abstractmethod
    def reset(self):
        """
        Reset the VLM model context and KV cache. If not reset, the model will skip the number of evaluated tokens and treat tokens after those as the new incremental tokens.
        If your past chat history changed, or you are starting a new chat, you should always reset the model before running generate.
        """
        pass

    def _process_image(self, image: Union[bytes, str, Path]) -> bytes:
        """Process image input to bytes format.
        
        Args:
            image: Image data as bytes, base64 string, or file path
            
        Returns:
            Image data as bytes
        """
        if isinstance(image, bytes):
            return image
        elif isinstance(image, str):
            # Check if it's a base64 string
            if image.startswith('data:image'):
                # Extract base64 data from data URL
                base64_data = image.split(',')[1] if ',' in image else image
                return base64.b64decode(base64_data)
            else:
                # Assume it's a file path
                with open(image, 'rb') as f:
                    return f.read()
        elif isinstance(image, Path):
            with open(image, 'rb') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
        

    @abstractmethod
    def apply_chat_template(
        self,
        messages: List[MultiModalMessage],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Apply the chat template to multimodal messages."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, g_cfg: GenerationConfig = GenerationConfig()) -> Generator[str, None, None]:
        """Generate text with streaming."""
        pass

    @abstractmethod
    def generate(self, prompt: str, g_cfg: GenerationConfig = GenerationConfig()) -> str:
        """
        Generate text without streaming.

        Args:
            prompt (str): The prompt to generate text from. For chat models, this is the chat messages after chat template is applied.
            g_cfg (GenerationConfig): Generation configuration.

        Returns:
            str: The generated text.
        """
        pass