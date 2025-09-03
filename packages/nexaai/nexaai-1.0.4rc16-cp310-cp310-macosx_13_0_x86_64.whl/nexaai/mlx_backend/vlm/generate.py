import argparse
import codecs
import contextlib
import functools
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import mlx.core as mx
import mlx.nn as nn
from mlx_lm.generate import maybe_quantize_kv_cache
from transformers import PreTrainedTokenizer

from .modeling.models import cache
from .modeling.prompt_utils import apply_chat_template
from .modeling.sample_utils import top_p_sampling
from .modeling.utils import (
    StoppingCriteria,
    apply_repetition_penalty,
    load,
    prepare_inputs,
    tree_reduce,
)

DEFAULT_MODEL_PATH = "mlx-community/gemma-3-4b-it-8bit"


def parse_media_from_input(user_input):
    """Parse quoted media files from user input and return prompt and media paths"""
    # Find all quoted strings (both single and double quotes)
    quoted_pattern = r'["\']([^"\']*)["\']'
    quoted_matches = re.findall(quoted_pattern, user_input)
    
    # Remove quoted strings from the input to get the actual prompt
    prompt = re.sub(quoted_pattern, '', user_input).strip()
    
    # Separate image and audio files based on extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    
    image_paths = []
    audio_paths = []
    
    for quoted_file in quoted_matches:
        if quoted_file:  # Skip empty quotes
            # Expand user path if it starts with ~
            if quoted_file.startswith('~'):
                quoted_file = os.path.expanduser(quoted_file)
            
            # Check if file exists
            if not os.path.exists(quoted_file):
                print(f"Warning: File '{quoted_file}' not found")
                continue
                
            file_ext = os.path.splitext(quoted_file.lower())[1]
            if file_ext in image_extensions:
                image_paths.append(quoted_file)
            elif file_ext in audio_extensions:
                audio_paths.append(quoted_file)
    
    return prompt, image_paths if image_paths else None, audio_paths if audio_paths else None


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate text from an image using a model."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL_PATH,
        help="The path to the local model directory or Hugging Face repo.",
    )
    return parser.parse_args()


# A stream on the default device just for generation
generation_stream = mx.new_stream(mx.default_device())


@contextlib.contextmanager
def wired_limit(model: nn.Module, streams: Optional[List[mx.Stream]] = None):
    """
    A context manager to temporarily change the wired limit.

    Note, the wired limit should not be changed during an async eval.  If an
    async eval could be running pass in the streams to synchronize with prior
    to exiting the context manager.
    """
    model_bytes = tree_reduce(
        lambda acc, x: acc + x.nbytes if isinstance(x, mx.array) else acc, model, 0
    )
    max_rec_size = mx.metal.device_info()["max_recommended_working_set_size"]
    if model_bytes > 0.9 * max_rec_size:
        model_mb = model_bytes // 2**20
        max_rec_mb = max_rec_size // 2**20
        print(
            f"[WARNING] Generating with a model that requires {model_mb} MB "
            f"which is close to the maximum recommended size of {max_rec_mb} "
            "MB. This can be slow. See the documentation for possible work-arounds: "
            "https://github.com/ml-explore/mlx-lm/tree/main#large-models"
        )
    old_limit = mx.set_wired_limit(max_rec_size)
    try:
        yield None
    finally:
        if streams is not None:
            for s in streams:
                mx.synchronize(s)
        else:
            mx.synchronize()
        mx.set_wired_limit(old_limit)


@dataclass
class GenerationResult:
    text: str
    token: Optional[int]
    logprobs: Optional[List[float]]
    prompt_tokens: int
    generation_tokens: int
    prompt_tps: float
    generation_tps: float
    peak_memory: float


def generate_step(
    input_ids: mx.array,
    model: nn.Module,
    pixel_values,
    mask,
    *,
    max_tokens: int = 256,
    temperature: float = 0.0,
    repetition_penalty: Optional[float] = None,
    repetition_context_size: Optional[int] = 20,
    top_p: float = 1.0,
    logit_bias: Optional[Dict[int, float]] = None,
    prompt_cache: Optional[List[Any]] = None,
    max_kv_size: Optional[int] = None,
    kv_bits: Optional[int] = None,
    kv_group_size: int = 64,
    quantized_kv_start: int = 0,
    **kwargs,
) -> Generator[Tuple[mx.array, mx.array], None, None]:
    """
    A generator producing token ids based on the given prompt from the model.

    Args:
        prompt (mx.array): The input prompt.
        model (nn.Module): The model to use for generation.
        temperature (float): The temperature for sampling, if 0 the argmax is used.
          Default: ``0``.
        repetition_penalty (float, optional): The penalty factor for repeating
          tokens.
        repetition_context_size (int, optional): The number of tokens to
          consider for repetition penalty. Default: ``20``.
        top_p (float, optional): Nulceus sampling, higher means model considers
          more less likely words.
        logit_bias (dictionary, optional): Additive logit bias.

    Yields:
        Generator[Tuple[mx.array, mx.array], None, None]: A generator producing
          one token and a vector of log probabilities.
    """

    quantize_cache_fn = functools.partial(
        maybe_quantize_kv_cache,
        quantized_kv_start=quantized_kv_start,
        kv_group_size=kv_group_size,
        kv_bits=kv_bits,
    )

    def sample(logits: mx.array) -> Tuple[mx.array, float]:
        if logit_bias:
            indices = mx.array(list(logit_bias.keys()))
            values = mx.array(list(logit_bias.values()))
            logits[:, indices] += values
        logprobs = logits - mx.logsumexp(logits)

        if temperature == 0:
            token = mx.argmax(logits, axis=-1)
        else:
            if top_p > 0 and top_p < 1.0:
                token = top_p_sampling(logits, top_p, temperature)
            else:
                token = mx.random.categorical(logits * (1 / temperature))

        return token, logprobs

    if repetition_penalty and (
        repetition_penalty < 0 or not isinstance(repetition_penalty, float)
    ):
        raise ValueError(
            f"repetition_penalty must be a non-negative float, got {repetition_penalty}"
        )

    y = input_ids
    # Create the KV cache for generation
    if prompt_cache is None:
        prompt_cache = cache.make_prompt_cache(
            model.language_model,
            max_kv_size=max_kv_size,
        )

    repetition_context = input_ids.reshape(-1).tolist()

    if repetition_context_size:
        repetition_context = repetition_context[-repetition_context_size:]

    def _step(y, **kwargs):
        with mx.stream(generation_stream):
            nonlocal repetition_context
            if "decoder_input_ids" in kwargs:
                outputs = model.language_model(
                    cache=prompt_cache,
                    **kwargs,
                )
            else:
                outputs = model.language_model(
                    y[None],
                    cache=prompt_cache,
                    **kwargs,
                )

            logits = outputs.logits[:, -1, :]

            if repetition_penalty:
                logits = apply_repetition_penalty(
                    logits, repetition_context, repetition_penalty
                )
                y, logprobs = sample(logits)
                repetition_context.append(y.item())
            else:
                y, logprobs = sample(logits)

            if repetition_context_size:
                if len(repetition_context) > repetition_context_size:
                    repetition_context = repetition_context[-repetition_context_size:]

            quantize_cache_fn(prompt_cache)
            return y, logprobs.squeeze(0)

    outputs = model(input_ids, pixel_values, cache=prompt_cache, mask=mask, **kwargs)

    logits = outputs.logits[:, -1, :]
    quantize_cache_fn(prompt_cache)
    y, logprobs = sample(logits)
    mx.async_eval(y)

    if outputs.cross_attention_states is not None:
        kwargs = {
            k: v
            for k, v in zip(
                ["cross_attention_states"], [outputs.cross_attention_states]
            )
        }
    elif outputs.encoder_outputs is not None:
        kwargs = {
            "decoder_input_ids": y[None],
            "encoder_outputs": outputs.encoder_outputs,
        }
    else:
        kwargs = {}

    n = 0
    while True:
        if n != max_tokens:
            next_y, next_logprobs = _step(y, **kwargs)
            mx.async_eval(next_y)
            if "decoder_input_ids" in kwargs:
                kwargs["decoder_input_ids"] = next_y[None]
            yield y.item(), logprobs
            y, logprobs = next_y, next_logprobs
        if n == max_tokens:
            break

        n += 1

        # Periodically clear cache to prevent memory accumulation
        if n % 256 == 0:  # Clear cache every 256 tokens
            mx.clear_cache()


def stream_generate(
    model: nn.Module,
    processor: PreTrainedTokenizer,
    prompt: str,
    image: Union[str, List[str]] = None,
    audio: Union[str, List[str]] = None,
    **kwargs,
) -> Union[str, Generator[str, None, None]]:
    """
    A generator producing text based on the given prompt from the model.

    Args:
        prompt (mx.array): The input prompt.
        model (nn.Module): The model to use for generation.
        max_tokens (int): The ma
        kwargs: The remaining options get passed to :func:`generate_step`.
          See :func:`generate_step` for more details.

    Yields:
        Generator[Tuple[mx.array, mx.array]]: A generator producing text.
    """
    tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor

    # Skip special tokens
    skip_special_tokens = kwargs.pop("skip_special_tokens", False)
    skip_special_token_ids = (
        set(tokenizer.all_special_ids)
        if skip_special_tokens and hasattr(tokenizer, "all_special_ids")
        else []
    )

    add_special_tokens = (
        not hasattr(processor, "chat_template")
        if model.config.model_type in ["gemma3", "gemma3n"]
        else True
    )

    resize_shape = kwargs.pop("resize_shape", None)
    image_token_index = getattr(model.config, "image_token_index", None)

    if kwargs.get("input_ids", None) is not None:
        input_ids = kwargs.pop("input_ids")
        pixel_values = kwargs.pop("pixel_values", None)
        mask = kwargs.pop("mask", None)
    else:
        inputs = prepare_inputs(
            processor,
            images=image,
            audio=audio,
            prompts=prompt,
            image_token_index=image_token_index,
            resize_shape=resize_shape,
            add_special_tokens=add_special_tokens,
        )
        input_ids = inputs.get("input_ids", None)
        pixel_values = inputs.get("pixel_values", None)
        mask = inputs.get("attention_mask", None)
        data_kwargs = {
            k: v
            for k, v in inputs.items()
            if k not in ["input_ids", "pixel_values", "attention_mask"]
        }
        kwargs.update(data_kwargs)

    with wired_limit(model, [generation_stream]):
        detokenizer = processor.detokenizer
        detokenizer.reset()
        tic = time.perf_counter()
        for n, (token, logprobs) in enumerate(
            generate_step(input_ids, model, pixel_values, mask, **kwargs)
        ):
            if n == 0:
                prompt_time = time.perf_counter() - tic
                prompt_tps = input_ids.size / prompt_time
                tic = time.perf_counter()

            # Stop generation if the token is in the eos_token_ids
            if tokenizer.stopping_criteria(token):
                break

            detokenizer.add_token(token, skip_special_token_ids=skip_special_token_ids)

            # Yield the last segment if streaming
            yield GenerationResult(
                text=detokenizer.last_segment,
                token=token,
                logprobs=logprobs,
                prompt_tokens=input_ids.size,
                generation_tokens=n + 1,
                prompt_tps=prompt_tps,
                generation_tps=(n + 1) / (time.perf_counter() - tic),
                peak_memory=mx.get_peak_memory() / 1e9,
            )

        detokenizer.finalize()
        yield GenerationResult(
            text=detokenizer.last_segment,
            token=token,
            logprobs=logprobs,
            prompt_tokens=input_ids.size,
            generation_tokens=n + 1,
            prompt_tps=prompt_tps,
            generation_tps=(n + 1) / (time.perf_counter() - tic),
            peak_memory=mx.get_peak_memory() / 1e9,
        )

        # Cleanup after generation
        mx.clear_cache()


def generate(
    model: nn.Module,
    processor: PreTrainedTokenizer,
    prompt: str,
    image: Union[str, List[str]] = None,
    audio: Union[str, List[str]] = None,
    verbose: bool = False,
    **kwargs,
) -> str:
    """
    Generate text from the model.

    Args:
       model (nn.Module): The language model.
       tokenizer (PreTrainedTokenizer): The tokenizer.
       prompt (str): The string prompt.
       temperature (float): The temperature for sampling (default 0).
       max_tokens (int): The maximum number of tokens (default 100).
       verbose (bool): If ``True``, print tokens and timing information
           (default ``False``).
       formatter (Optional[Callable]): A function which takes a token and a
           probability and displays it.
       repetition_penalty (float, optional): The penalty factor for repeating tokens.
       repetition_context_size (int, optional): The number of tokens to consider for repetition penalty.
    """

    if verbose:
        print("=" * 10)
        files = []
        if image is not None:
            files.extend(image)
        if audio is not None:
            files.extend(audio)
        if kwargs.get("video") is not None:
            files.extend(kwargs.get("video"))

        print(f"Files: {files}", "\n")

        print("Prompt:", prompt)

    text = ""
    last_response = None

    eos_tokens = kwargs.get("eos_tokens", None)
    stopping_criteria = kwargs.get("stopping_criteria", None)

    # Get the tokenizer
    tokenizer = processor.tokenizer if hasattr(processor, "tokenizer") else processor

    # Add custom EOS tokens to the stopping criteria
    if eos_tokens is not None:
        tokenizer.stopping_criteria.add_eos_token_ids(eos_tokens)

    # Use custom stopping criteria
    elif stopping_criteria is not None:
        if isinstance(stopping_criteria, StoppingCriteria) or callable(
            stopping_criteria
        ):
            tokenizer.stopping_criteria = stopping_criteria
        else:
            raise ValueError(
                "stopping_criteria must be an instance of StoppingCriteria or a callable"
            )
    else:
        tokenizer.stopping_criteria.reset(model.config.eos_token_id)

    for response in stream_generate(model, processor, prompt, image, audio, **kwargs):
        if verbose:
            print(response.text, end="", flush=True)
        text += response.text
        last_response = response

    if verbose:
        print("\n" + "=" * 10)
        if len(text) == 0:
            print("No text generated for this prompt")
            return
        print(
            f"Prompt: {last_response.prompt_tokens} tokens, "
            f"{last_response.prompt_tps:.3f} tokens-per-sec"
        )
        print(
            f"Generation: {last_response.generation_tokens} tokens, "
            f"{last_response.generation_tps:.3f} tokens-per-sec"
        )
        print(f"Peak memory: {last_response.peak_memory:.3f} GB")

    usage_stats = {
        "input_tokens": last_response.prompt_tokens,
        "output_tokens": last_response.generation_tokens,
        "total_tokens": last_response.prompt_tokens + last_response.generation_tokens,
        "prompt_tps": last_response.prompt_tps,
        "generation_tps": last_response.generation_tps,
        "peak_memory": last_response.peak_memory,
    }

    return text, usage_stats


def main():
    args = parse_arguments()
    
    # Load model and processor
    model, processor = load(args.model, None)
    config = model.config

    # Initialize chat history
    chat = []
    
    print("Multi-round conversation started. Type 'exit' or 'quit' to stop.")
    print("You can include image/audio files in quotes, e.g.: 'what does this image mean \"/path/to/image.jpg\"'")
    print("=" * 50)
    
    # Main chat loop
    while True:
        try:
            user_input = input("User: ").strip()
            
            # Exit conditions
            if user_input.lower() in ['exit', 'quit', '']:
                break
            
            # Parse media files from user input
            prompt_text, image_paths, audio_paths = parse_media_from_input(user_input)
            
            # If no text prompt after parsing, use the original input
            if not prompt_text.strip():
                prompt_text = user_input
                image_paths = None
                audio_paths = None
            
            # Add user message to chat history
            chat.append({"role": "user", "content": prompt_text})
            
            # Calculate number of images for chat template
            num_images = len(image_paths) if image_paths else 0
            num_audios = len(audio_paths) if audio_paths else 0
            
            # Apply chat template
            formatted_prompt = apply_chat_template(
                processor, config, chat, num_images=num_images, num_audios=num_audios
            )
            
            # Generate response
            response = ""
            print("Assistant: ", end="", flush=True)
            
            for chunk in stream_generate(
                model,
                processor,
                formatted_prompt,
                image_paths,
                audio_paths,
                max_tokens=100,
                temperature=0.7,
                top_p=0.9,
                verbose=True,
            ):
                response += chunk.text
                print(chunk.text, end="", flush=True)
            
            print()  # New line after response
            
            # Add assistant response to chat history
            chat.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\nConversation interrupted by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue


if __name__ == "__main__":
    main()
