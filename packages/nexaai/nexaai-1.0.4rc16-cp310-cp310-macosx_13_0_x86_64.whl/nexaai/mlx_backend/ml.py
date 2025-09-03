# This file defines the python interface that c-lib expects from a python backend

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypedDict,
)

# --------------------------------------------------------------------------------------
# Core aliases & callback protocols
# --------------------------------------------------------------------------------------

Path = str

LogCallback = Callable[[str], None]


class TokenCallback(Protocol):
    def __call__(self, token: str, user_data: Any) -> bool: ...


# --------------------------------------------------------------------------------------
# Core module functions
# --------------------------------------------------------------------------------------

def init() -> None:
    """Initialize the ML module."""
    pass


def deinit() -> None:
    """Deinitialize the ML module."""
    pass


def set_log(callback: LogCallback) -> None:
    """Set the logging callback."""
    pass


def log(message: str) -> None:
    """Log a message."""
    pass


def model_config_default() -> ModelConfig:
    """Get default model configuration with sensible defaults."""
    return ModelConfig()


# --------------------------------------------------------------------------------------
# Basic data structures
# --------------------------------------------------------------------------------------

@dataclass
class Image:
    """Image data structure."""
    data: List[float]  # width × height × channels
    width: int
    height: int
    channels: int  # 3 = RGB, 4 = RGBA


@dataclass
class Audio:
    """Audio data structure."""
    data: List[float]  # num_samples × channels
    sample_rate: int
    channels: int
    num_samples: int


@dataclass
class Video:
    """Video data structure."""
    data: List[float]  # width × height × channels × num_frames
    width: int
    height: int
    channels: int
    num_frames: int


# --------------------------------------------------------------------------------------
# Language-model structures
# --------------------------------------------------------------------------------------

@dataclass
class ModelConfig:
    """Configuration for model parameters."""
    n_ctx: int = 0  # text context, 0 = from model
    n_threads: int = 0  # number of threads to use for generation
    n_threads_batch: int = 0  # number of threads to use for batch processing
    n_batch: int = 0  # logical maximum batch size that can be submitted to llama_decode
    n_ubatch: int = 0  # physical maximum batch size
    n_seq_max: int = 0  # max number of sequences (i.e. distinct states for recurrent models)
    chat_template_path: Optional[Path] = None  # path to chat template file, optional
    chat_template_content: Optional[str] = None  # content of chat template file, optional


@dataclass
class SamplerConfig:
    """Configuration for text sampling."""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    min_p: float = 0.0  # Minimum probability for nucleus sampling
    repetition_penalty: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: int = -1  # –1 for random
    grammar_path: Optional[Path] = None
    grammar_string: Optional[str] = None  # Optional grammar string (BNF-like format)


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 512
    stop: Sequence[str] = field(default_factory=tuple)
    n_past: int = 0
    sampler_config: Optional[SamplerConfig] = None
    image_paths: Optional[Sequence[Path]] = None  # Array of image paths for VLM (None if none)
    audio_paths: Optional[Sequence[Path]] = None  # Array of audio paths for VLM (None if none)


@dataclass
class ChatMessage:
    """A chat message with role and content."""
    role: str  # "user" | "assistant" | "system"
    content: str


class ToolFunction(TypedDict):
    name: str
    description: str
    parameters_json: str


class Tool(TypedDict):
    type: str
    function: ToolFunction


# --------------------------------------------------------------------------------------
# Embedding / rerank / diffusion / OCR / ASR / TTS utilities
# --------------------------------------------------------------------------------------

@dataclass
class EmbeddingConfig:
    """Configuration for embeddings."""
    batch_size: int = 1
    normalize: bool = True
    normalize_method: str = "l2"  # "l2" | "mean" | "none"


@dataclass
class RerankConfig:
    """Configuration for reranking."""
    batch_size: int = 1
    normalize: bool = True
    normalize_method: str = "softmax"  # "softmax" | "min-max" | "none"


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
    prompts: str | List[str]
    negative_prompts: str | List[str] | None = None
    height: int = 512
    width: int = 512
    sampler_config: Optional[ImageSamplerConfig] = None
    lora_id: int = -1  # –1 for none
    init_image: Optional[Image] = None
    strength: float = 1.0


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
    config_path: Optional[Path] = None


@dataclass
class ASRConfig:
    """Configuration for ASR."""
    timestamps: str = "none"  # "none" | "segment" | "word"
    beam_size: int = 5
    stream: bool = False


@dataclass
class ASRResult:
    """Result from ASR processing."""
    transcript: str
    confidence_scores: Sequence[float]
    timestamps: Sequence[Tuple[float, float]]
    duration_us: float


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


# --------------------------------------------------------------------------------------
# Computer Vision structures
# --------------------------------------------------------------------------------------

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
    image_paths: Optional[List[Path]] = None  # Output image paths
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


# --------------------------------------------------------------------------------------
# LLM
# --------------------------------------------------------------------------------------

class LLM(ABC):
    """Abstract base class for Large Language Models."""

    def __init__(
        self,
        model_path: Path,
        tokenizer_path: Path,
        config: ModelConfig,
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.config = config
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the model state."""
        pass

    # Tokenization
    @abstractmethod
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs."""
        pass

    @abstractmethod
    def decode(self, token_ids: Sequence[int]) -> str:
        """Decode token IDs to text."""
        pass

    # KV-cache
    @abstractmethod
    def save_kv_cache(self, path: Path) -> bool:
        """Save KV cache to file."""
        pass

    @abstractmethod
    def load_kv_cache(self, path: Path) -> bool:
        """Load KV cache from file."""
        pass

    # LoRA
    @abstractmethod
    def set_lora(self, lora_id: int) -> None:
        """Set active LoRA adapter."""
        pass

    @abstractmethod
    def add_lora(self, lora_path: Path) -> int:
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

    # Sampler
    @abstractmethod
    def set_sampler(self, config: SamplerConfig) -> None:
        """Set sampler configuration."""
        pass

    @abstractmethod
    def reset_sampler(self) -> None:
        """Reset sampler to default configuration."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig],
        on_token: TokenCallback,
        user_data: Any = None,
    ) -> str:
        """Generate text with streaming callback."""
        pass

    @abstractmethod
    def get_chat_template(self, template_name: str) -> str:
        """Get chat template by name."""
        pass

    @abstractmethod
    def apply_chat_template(self, messages: Sequence[ChatMessage], tools: Optional[Sequence[Tool]] = None, enable_thinking: bool = True) -> str:
        """Apply chat template to messages with optional tools support."""
        pass

    # Embeddings
    @abstractmethod
    def embed(
        self,
        texts: Sequence[str],
        config: Optional[EmbeddingConfig] = None,
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        pass


# --------------------------------------------------------------------------------------
# VLM (Vision-Language Model)
# --------------------------------------------------------------------------------------

class VLM(ABC):
    """Abstract base class for Vision-Language Models."""

    def __init__(
        self,
        model_path: Path,
        mmproj_path: Path,
        context_length: int,
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.mmproj_path = mmproj_path
        self.context_length = context_length
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the model state."""
        pass

    # Tokenization
    @abstractmethod
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs."""
        pass

    @abstractmethod
    def decode(self, token_ids: Sequence[int]) -> str:
        """Decode token IDs to text."""
        pass

    # Sampler
    @abstractmethod
    def set_sampler(self, config: SamplerConfig) -> None:
        """Set sampler configuration."""
        pass

    @abstractmethod
    def reset_sampler(self) -> None:
        """Reset sampler to default configuration."""
        pass

    # Generation
    @abstractmethod
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def generate_multimodal(
        self,
        prompt: str,
        image_paths: Optional[Sequence[Path]] = None,
        audio_paths: Optional[Sequence[Path]] = None,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """Generate text from prompt with multiple images and audio."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig],
        on_token: TokenCallback,
        user_data: Any = None,
    ) -> str:
        """Generate text with streaming callback."""
        pass

    @abstractmethod
    def generate_stream_multimodal(
        self,
        prompt: str,
        image_paths: Optional[Sequence[Path]] = None,
        audio_paths: Optional[Sequence[Path]] = None,
        config: Optional[GenerationConfig] = None,
        on_token: Optional[TokenCallback] = None,
        user_data: Any = None,
    ) -> str:
        """Generate text from prompt with multiple images and audio using streaming callback."""
        pass

    @abstractmethod
    def get_chat_template(self, template_name: str) -> str:
        """Get chat template by name."""
        pass

    @abstractmethod
    def apply_chat_template(self, messages: Sequence[ChatMessage], tools: Optional[Sequence[Tool]] = None, enable_thinking: bool = True) -> str:
        """Apply chat template to messages with optional tools support."""
        pass

    # Embeddings
    @abstractmethod
    def embed(
        self,
        texts: Sequence[str],
        config: Optional[EmbeddingConfig] = None,
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        pass


# --------------------------------------------------------------------------------------
# Embedding Model
# --------------------------------------------------------------------------------------

class Embedder(ABC):
    """Abstract base class for embedding models."""

    def __init__(
        self,
        model_path: Path,
        tokenizer_path: Path,
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def load_model(self, model_path: Path, extra_data: Any = None) -> bool:
        """Load model from path."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the model."""
        pass

    @abstractmethod
    def embed(
        self,
        texts: Sequence[str],
        config: Optional[EmbeddingConfig] = None,
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        pass

    @abstractmethod
    def embedding_dim(self) -> int:
        """Get embedding dimension."""
        pass

    @abstractmethod
    def set_lora(self, lora_id: int) -> None:
        """Set active LoRA adapter."""
        pass

    @abstractmethod
    def add_lora(self, lora_path: Path) -> int:
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


# --------------------------------------------------------------------------------------
# Reranker Model
# --------------------------------------------------------------------------------------

class Reranker(ABC):
    """Abstract base class for reranker models."""

    def __init__(
        self,
        model_path: Path,
        tokenizer_path: Path,
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def load_model(self, model_path: Path, extra_data: Any = None) -> bool:
        """Load model from path."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the model."""
        pass

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        config: Optional[RerankConfig] = None,
    ) -> List[float]:
        """Rerank documents given a query."""
        pass


# --------------------------------------------------------------------------------------
# Image generation
# --------------------------------------------------------------------------------------

class ImageGen(ABC):
    """Abstract base class for image generation models."""

    def __init__(
        self,
        model_path: Path,
        scheduler_config_path: Path,
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.scheduler_config_path = scheduler_config_path
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def load_model(self, model_path: Path, extra_data: Any = None) -> bool:
        """Load model from path."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the model."""
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
    def add_lora(self, lora_path: Path) -> int:
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


# --------------------------------------------------------------------------------------
# Computer vision – Generic CV Model
# --------------------------------------------------------------------------------------

class CVModel(ABC):
    """Abstract base class for generic computer vision models."""

    def __init__(self, config: CVModelConfig, device: Optional[str] = None) -> None:
        self.config = config
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def infer(self, input_image_path: str) -> CVResults:
        """Perform inference on image."""
        pass


# --------------------------------------------------------------------------------------
# Speech recognition – ASR
# --------------------------------------------------------------------------------------

class ASR(ABC):
    """Abstract base class for Automatic Speech Recognition models."""

    def __init__(
        self,
        model_path: Path,
        tokenizer_path: Optional[Path],
        language: Optional[str],
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.language = language
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the model."""
        pass

    @abstractmethod
    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        config: Optional[ASRConfig] = None,
    ) -> ASRResult:
        """Transcribe audio file to text."""
        pass

    @abstractmethod
    def list_supported_languages(self) -> List[str]:
        """List supported languages."""
        pass


# --------------------------------------------------------------------------------------
# Speech synthesis – TTS
# --------------------------------------------------------------------------------------

class TTS(ABC):
    """Abstract base class for Text-to-Speech models."""

    def __init__(
        self,
        model_path: Path,
        vocoder_path: Path,
        device: Optional[str] = None,
    ) -> None:
        self.model_path = model_path
        self.vocoder_path = vocoder_path
        self.device = device

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the model and free resources."""
        pass

    @abstractmethod
    def synthesize(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
        output_path: Optional[Path] = None,
    ) -> TTSResult:
        """Synthesize speech from text and save to filesystem."""
        pass

    @abstractmethod
    def list_available_voices(self) -> List[str]:
        """List available voices."""
        pass
