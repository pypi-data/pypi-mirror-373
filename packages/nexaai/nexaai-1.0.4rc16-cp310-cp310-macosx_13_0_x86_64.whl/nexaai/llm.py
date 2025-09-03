from typing import Generator, Optional, Union
from abc import abstractmethod
import queue
import threading

from nexaai.common import ModelConfig, GenerationConfig, ChatMessage, PluginID
from nexaai.base import BaseModel

class LLM(BaseModel):
    def __init__(self, m_cfg: ModelConfig = ModelConfig()):
        """Initialize base LLM class."""
        self._m_cfg = m_cfg
        self._cancel_event = threading.Event()  # New attribute to control cancellation

    @classmethod
    def _load_from(cls,
                   local_path: str,
                   tokenizer_path: Optional[str] = None,
                   m_cfg: ModelConfig = ModelConfig(),
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None
        ) -> 'LLM':
        """Load model from local path, routing to appropriate implementation."""
        # Check plugin_id value for routing - handle both enum and string
        plugin_value = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        if plugin_value == "mlx":
            from nexaai.llm_impl.mlx_llm_impl import MLXLLMImpl
            return MLXLLMImpl._load_from(local_path, tokenizer_path, m_cfg, plugin_id, device_id)
        else:
            from nexaai.llm_impl.pybind_llm_impl import PyBindLLMImpl
            return PyBindLLMImpl._load_from(local_path, tokenizer_path, m_cfg, plugin_id, device_id)

    def cancel_generation(self):
        """Signal to cancel any ongoing stream generation."""
        self._cancel_event.set()

    def reset_cancel(self):
        """Reset the cancel event. Call before starting a new generation if needed."""
        self._cancel_event.clear()

    @abstractmethod
    def apply_chat_template(self, messages: list[ChatMessage], tools: Optional[str] = None, enable_thinking: bool = True, add_generation_prompt: bool = True) -> str:
        """Apply the chat template to messages."""
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

    @abstractmethod
    def save_kv_cache(self, path: str):
        """
        Save the key-value cache to the file.

        Args:
            path (str): The path to the file.
        """
        pass

    @abstractmethod
    def load_kv_cache(self, path: str):
        """
        Load the key-value cache from the file.

        Args:
            path (str): The path to the file.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the LLM model context and KV cache. If not reset, the model will skip the number of evaluated tokens and treat tokens after those as the new incremental tokens.
        If your past chat history changed, or you are starting a new chat, you should always reset the model before running generate.
        """
        pass
