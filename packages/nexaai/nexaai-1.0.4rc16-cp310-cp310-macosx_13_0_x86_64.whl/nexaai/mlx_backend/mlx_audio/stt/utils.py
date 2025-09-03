# modified

import importlib
import json
import logging
from pathlib import Path
from typing import List, Optional

import mlx.core as mx
import numpy as np
import soundfile as sf
from scipy import signal

SAMPLE_RATE = 16000

MODEL_REMAPPING = {}
MAX_FILE_SIZE_GB = 5
MODEL_CONVERSION_DTYPES = ["float16", "bfloat16", "float32"]


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    gcd = np.gcd(orig_sr, target_sr)
    up = target_sr // gcd
    down = orig_sr // gcd
    resampled = signal.resample_poly(audio, up, down, padtype="edge")
    return resampled


def load_audio(
    file: str = Optional[str],
    sr: int = SAMPLE_RATE,
    from_stdin=False,
    dtype: mx.Dtype = mx.float32,
):
    """
    Open an audio file and read as mono waveform, resampling as necessary

    Parameters
    ----------
    file: str
        The audio file to open

    sr: int
        The sample rate to resample the audio if necessary

    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """
    audio, sample_rate = sf.read(file, always_2d=True)
    if sample_rate != sr:
        audio = resample_audio(audio, sample_rate, sr)
    return mx.array(audio, dtype=dtype).mean(axis=1)


def get_model_path(path: str) -> Path:
    """
    Ensures the model is available locally. Only works with local paths.

    Args:
        path (str): The local path to the model.

    Returns:
        Path: The path to the model.
        
    Raises:
        FileNotFoundError: If the local path does not exist.
    """
    model_path = Path(path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model path '{path}' does not exist locally. Please ensure the model is available at the specified path.")

    return model_path


# Get a list of all available model types from the models directory
def get_available_models():
    """
    Get a list of all available TTS model types by scanning the models directory.

    Returns:
        List[str]: A list of available model type names
    """
    models_dir = Path(__file__).parent / "models"
    available_models = []

    if models_dir.exists() and models_dir.is_dir():
        for item in models_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                available_models.append(item.name)

    return available_models


def load_config(model_path: Path) -> dict:
    """
    Load the model configuration from config.json.

    Args:
        model_path (Path): Path to the model directory.

    Returns:
        dict: The model configuration.

    Raises:
        FileNotFoundError: If config.json is not found.
    """
    try:
        with open(model_path / "config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        logging.error(f"Config file not found in {model_path}")
        raise
    return config


def get_model_and_args(model_type: str):
    """
    Retrieve the model architecture module based on the model type.

    Args:
        model_type (str): The type of model to load (e.g., "whisper", "parakeet").

    Returns:
        Tuple[module, str]: A tuple containing:
            - The imported architecture module
            - The resolved model_type string after remapping

    Raises:
        ValueError: If the model type is not supported (module import fails).
    """
    # Check if the model type is in the remapping
    model_type = MODEL_REMAPPING.get(model_type, model_type)

    try:
        arch = importlib.import_module(f"mlx_audio.stt.models.{model_type}")
    except ImportError:
        msg = f"Model type {model_type} not supported."
        logging.error(msg)
        raise ValueError(msg)

    return arch, model_type


def load_model(model_path: str, lazy: bool = False, strict: bool = True, **kwargs):
    """
    Load and initialize the model from a given path.

    Args:
        model_path (str): The path to load the model from.
        lazy (bool): If False eval the model parameters to make sure they are
            loaded in memory before returning, otherwise they will be loaded
            when needed. Default: ``False``

    Returns:
        nn.Module: The loaded and initialized model.

    Raises:
        FileNotFoundError: If the weight files (.safetensors) are not found.
        ValueError: If the model class or args class are not found or cannot be instantiated.
    """
    # Convert to Path object for easier handling
    if isinstance(model_path, str):
        model_path = Path(model_path)
    elif not isinstance(model_path, Path):
        raise ValueError(f"Invalid model path type: {type(model_path)}")

    # Load configuration to get model_type
    config = load_config(model_path)
    model_type = config.get("model_type")
    
    if model_type is None:
        # Fallback: try to infer model_type from the path name
        directory_name = model_path.name
        parts = directory_name.split("-")
        
        model_class = None
        for part in parts:
            try:
                model_class, model_type = get_model_and_args(part)
                break
            except ValueError:
                continue
        
        if model_class is None:
            raise ValueError(f"Model type not found in config.json at {model_path} and could not be inferred from path name '{directory_name}'")
    else:
        model_class, model_type = get_model_and_args(model_type)
    model = model_class.Model.from_pretrained(model_path)

    if not lazy:
        model.eval()

    return model
