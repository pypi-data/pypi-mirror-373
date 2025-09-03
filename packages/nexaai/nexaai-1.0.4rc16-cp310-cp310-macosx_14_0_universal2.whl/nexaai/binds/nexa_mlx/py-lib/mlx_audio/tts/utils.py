import glob
import importlib
import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Tuple, Union

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten
from mlx_lm.convert import mixed_quant_predicate_builder
from mlx_lm.utils import dequantize_model, quantize_model, save_config, save_model

MODEL_REMAPPING = {"outetts": "outetts", "spark": "spark", "sam": "sesame"}
MAX_FILE_SIZE_GB = 5
MODEL_CONVERSION_DTYPES = ["float16", "bfloat16", "float32"]


def get_model_path(path: str, revision: Optional[str] = None) -> Path:
    """
    Ensures the model is available locally. Only works with local paths.

    Args:
        path_or_hf_repo (str): The local path to the model.
        revision (str, optional): Ignored for local paths, kept for compatibility.

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


def get_model_and_args(model_type: str, model_name: List[str]):
    """
    Retrieve the model architecture module based on the model type and name.

    This function attempts to find the appropriate model architecture by:
    1. Checking if the model_type is directly in the MODEL_REMAPPING dictionary
    2. Looking for partial matches in segments of the model_name

    Args:
        model_type (str): The type of model to load (e.g., "outetts").
        model_name (List[str]): List of model name components that might contain
                               remapping information.

    Returns:
        Tuple[module, str]: A tuple containing:
            - The imported architecture module
            - The resolved model_type string after remapping

    Raises:
        ValueError: If the model type is not supported (module import fails).
    """
    # Stage 1: Check if the model type is in the remapping
    model_type = MODEL_REMAPPING.get(model_type, model_type)

    # Stage 2: Check for partial matches in segments of the model name
    models = get_available_models()
    if model_name is not None:
        for part in model_name:
            # First check if the part matches an available model directory name
            if part in models:
                model_type = part

            # Then check if the part is in our custom remapping dictionary
            if part in MODEL_REMAPPING:
                model_type = MODEL_REMAPPING[part]
                break

    try:
        arch = importlib.import_module(f"mlx_audio.tts.models.{model_type}")
    except ImportError:
        msg = f"Model type {model_type} not supported."
        logging.error(msg)
        raise ValueError(msg)

    return arch, model_type


def load_config(model_path: Union[str, Path], **kwargs) -> dict:
    """Load model configuration from a local path.

    Args:
        model_path: Local path to load config from
        **kwargs: Additional keyword arguments (ignored for local loading)

    Returns:
        dict: Model configuration

    Raises:
        FileNotFoundError: If config.json is not found at the path
    """
    if isinstance(model_path, str):
        model_path = get_model_path(model_path)

    try:
        with open(model_path / "config.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Config not found at {model_path}") from exc


def load_model(
    model_path: Path, lazy: bool = False, strict: bool = True, **kwargs
) -> nn.Module:
    """
    Load and initialize the model from a given path.

    Args:
        model_path (Path): The path to load the model from.
        lazy (bool): If False eval the model parameters to make sure they are
            loaded in memory before returning, otherwise they will be loaded
            when needed. Default: ``False``

    Returns:
        nn.Module: The loaded and initialized model.

    Raises:
        FileNotFoundError: If the weight files (.safetensors) are not found.
        ValueError: If the model class or args class are not found or cannot be instantiated.
    """
    model_name = None
    if isinstance(model_path, str):
        model_name = model_path.lower().split("/")[-1].split("-")
        model_path = get_model_path(model_path)
    elif isinstance(model_path, Path):
        model_name = model_path.name.lower().split("-")
    else:
        raise ValueError(f"Invalid model path type: {type(model_path)}")

    config = load_config(model_path, **kwargs)
    config["tokenizer_name"] = model_path

    # Determine model_type from config or model_name
    model_type = config.get("model_type", None)
    if model_type is None:
        model_type = model_name[0].lower() if model_name is not None else None
        
    # TODO: remove this check once we cleaned other models.
    if model_type != "kokoro":
        raise ValueError(f"Model type {model_type} not supported. Only kokoro is supported for now.")

    quantization = config.get("quantization", None)

    weight_files = glob.glob(str(model_path / "*.safetensors"))
    if not weight_files:
        # Check in LLM directory if no safetensors found in the main directory
        # For Spark model
        weight_files = glob.glob(str(model_path / "LLM" / "*.safetensors"))

    if not weight_files:
        logging.error(f"No safetensors found in {model_path}")
        message = f"""
No safetensors found in {model_path}
Please ensure that the model directory contains the required .safetensors weight files.
The model directory should contain:
- config.json (model configuration)
- *.safetensors (model weights)
- Any other required model files

If you have a PyTorch model, you may need to convert it to safetensors format first.
        """
        raise FileNotFoundError(message)

    weights = {}
    for wf in weight_files:
        weights.update(mx.load(wf))

    model_class, model_type = get_model_and_args(
        model_type=model_type, model_name=model_name
    )

    # Get model config from model class if it exists, otherwise use the config
    model_config = (
        model_class.ModelConfig.from_dict(config)
        if hasattr(model_class, "ModelConfig")
        else config
    )

    if model_config is not None and hasattr(model_config, "model_path"):
        # For Spark model
        model_config.model_path = model_path

    model = model_class.Model(model_config)
    quantization = config.get("quantization", None)
    if quantization is None:
        weights = model.sanitize(weights)

    if (quantization := config.get("quantization", None)) is not None:

        def get_class_predicate(p, m):
            # Handle custom per layer quantizations
            if p in config["quantization"]:
                return config["quantization"][p]
            if not hasattr(m, "to_quantized"):
                return False
            # Skip layers not divisible by 64
            if hasattr(m, "weight") and m.weight.size % 64 != 0:
                return False
            # Handle legacy models which may not have everything quantized
            return f"{p}.scales" in weights

        nn.quantize(
            model,
            group_size=quantization["group_size"],
            bits=quantization["bits"],
            class_predicate=get_class_predicate,
        )

    model.load_weights(list(weights.items()), strict=strict)

    if not lazy:
        mx.eval(model.parameters())

    model.eval()
    return model


def convert(
    hf_path: str,
    mlx_path: str = "mlx_model",
    quantize: bool = False,
    q_group_size: int = 64,
    q_bits: int = 4,
    dtype: str = None,
    revision: Optional[str] = None,
    dequantize: bool = False,
    trust_remote_code: bool = True,
    quant_predicate: Optional[str] = None,
):
    print("[INFO] Loading")
    model_path = get_model_path(hf_path, revision=revision)
    model = load_model(model_path, lazy=True, trust_remote_code=trust_remote_code)
    config = load_config(model_path, trust_remote_code=trust_remote_code)

    if isinstance(quant_predicate, str):
        quant_predicate = mixed_quant_predicate_builder(quant_predicate, model)

    # Get model-specific quantization predicate if available
    model_quant_predicate = getattr(
        model, "model_quant_predicate", lambda p, m, config: True
    )

    # Define base quantization requirements
    def base_quant_requirements(p, m, config):
        return (
            hasattr(m, "weight")
            and m.weight.shape[-1] % 64 == 0  # Skip layers not divisible by 64
            and hasattr(m, "to_quantized")
            and model_quant_predicate(p, m, config)
        )

    # Combine with user-provided predicate if available
    if quant_predicate is None:
        quant_predicate = base_quant_requirements
    else:
        original_predicate = quant_predicate
        quant_predicate = lambda p, m, config: (
            base_quant_requirements(p, m, config) and original_predicate(p, m, config)
        )

    weights = dict(tree_flatten(model.parameters()))

    if dtype is None:
        dtype = config.get("torch_dtype", None)
    if dtype in MODEL_CONVERSION_DTYPES:
        print("[INFO] Using dtype:", dtype)
        dtype = getattr(mx, dtype)
        weights = {k: v.astype(dtype) for k, v in weights.items()}

    if quantize and dequantize:
        raise ValueError("Choose either quantize or dequantize, not both.")

    if quantize:
        print("[INFO] Quantizing")
        model.load_weights(list(weights.items()))
        weights, config = quantize_model(
            model, config, q_group_size, q_bits, quant_predicate=quant_predicate
        )

    if dequantize:
        print("[INFO] Dequantizing")
        model = dequantize_model(model)
        weights = dict(tree_flatten(model.parameters()))

    if isinstance(mlx_path, str):
        mlx_path = Path(mlx_path)

    # Ensure the destination directory for MLX model exists before copying files
    mlx_path.mkdir(parents=True, exist_ok=True)

    # Copy Python and JSON files from the model path to the MLX path
    for pattern in ["*.py", "*.json", "*.wav", "*.pt", "*.safetensors", "*.yaml"]:
        files = glob.glob(str(model_path / pattern))
        for file in files:
            shutil.copy(file, mlx_path)

        # Check files in subdirectories up to two levels deep
        subdir_files = glob.glob(str(model_path / "**" / pattern), recursive=True)
        for file in subdir_files:
            rel_path = Path(file).relative_to(model_path)
            # Create subdirectories if they don't exist
            dest_dir = mlx_path / rel_path.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(file, dest_dir)

    save_model(mlx_path, model, donate_model=True)

    save_config(config, config_path=mlx_path / "config.json")
