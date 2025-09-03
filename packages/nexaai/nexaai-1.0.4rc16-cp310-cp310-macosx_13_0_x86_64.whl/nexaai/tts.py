from typing import List, Optional, Union
from abc import abstractmethod
from dataclasses import dataclass

from nexaai.base import BaseModel
from nexaai.common import PluginID


@dataclass
class TTSConfig:
    """Configuration for TTS."""
    voice: str = "default"
    speed: float = 1.0
    seed: int = -1  # –1 for random
    sample_rate: int = 22050


@dataclass
class TTSSamplerConfig:
    """Configuration for TTS sampling."""
    temperature: float = 1.0
    noise_scale: float = 0.667
    length_scale: float = 1.0


@dataclass
class TTSResult:
    """Result from TTS processing."""
    audio_path: str  # Path where the synthesized audio is saved
    duration_seconds: float
    sample_rate: int
    channels: int
    num_samples: int


class TTS(BaseModel):
    """Abstract base class for Text-to-Speech models."""

    def __init__(self):
        """Initialize base TTS class."""
        pass

    @classmethod
    def _load_from(cls,
                   model_path: str,
                   vocoder_path: str,
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None
        ) -> 'TTS':
        """Load TTS model from local path, routing to appropriate implementation."""
        # Check plugin_id value for routing - handle both enum and string
        plugin_value = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        if plugin_value == "mlx":
            from nexaai.tts_impl.mlx_tts_impl import MLXTTSImpl
            return MLXTTSImpl._load_from(model_path, vocoder_path, plugin_id, device_id)
        else:
            from nexaai.tts_impl.pybind_tts_impl import PyBindTTSImpl
            return PyBindTTSImpl._load_from(model_path, vocoder_path, plugin_id, device_id)

    @abstractmethod
    def synthesize(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
        output_path: Optional[str] = None,
    ) -> TTSResult:
        """Synthesize speech from text and save to filesystem."""
        pass

    @abstractmethod
    def list_available_voices(self) -> List[str]:
        """List available voices."""
        pass
