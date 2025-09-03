from dataclasses import dataclass
from typing import TypedDict, Literal, Optional, List
from enum import Enum


class PluginID(str, Enum):
    """Enum for plugin identifiers."""
    MLX = "mlx"
    LLAMA_CPP = "llama_cpp"


class ChatMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

class MultiModalMessageContent(TypedDict):
    type: Literal["text", "image", "audio", "video"]
    text: Optional[str]
    url: Optional[str]
    path: Optional[str]

class MultiModalMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: List[MultiModalMessageContent] 


@dataclass
class SamplerConfig:
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    repetition_penalty: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: int = -1
    grammar_path: str = None
    grammar_string: str = None

@dataclass
class GenerationConfig:
    max_tokens: int = 1024
    stop_words: list[str] = None
    sampler_config: SamplerConfig = None
    image_paths: list[str] = None
    audio_paths: list[str] = None

@dataclass
class ModelConfig:
    n_ctx: int = 4096
    n_threads: int = None
    n_threads_batch: int = None
    n_batch: int = 512
    n_ubatch: int = 512
    n_seq_max: int = 1
    n_gpu_layers: int = 999
    chat_template_path: str = None
    chat_template_content: str = None


@dataclass(frozen=True) # Read-only
class ProfilingData:
    start_time: int
    end_time: int
    prompt_start_time: int = None
    prompt_end_time: int = None
    decode_start_time: int = None
    decode_ent_time: int = None
    first_token_time: int = None
