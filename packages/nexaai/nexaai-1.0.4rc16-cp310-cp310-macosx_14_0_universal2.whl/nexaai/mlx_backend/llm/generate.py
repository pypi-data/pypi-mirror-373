import argparse
from mlx_lm.models.cache import make_prompt_cache
import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_reduce
from transformers import PreTrainedTokenizer
from mlx_lm.models import cache
from mlx_lm.models.cache import (
    QuantizedKVCache,
    load_prompt_cache,
)
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tokenizer_utils import TokenizerWrapper
from mlx_lm.utils import does_model_support_input_embeddings, load
from mlx_lm.generate import stream_generate

DEFAULT_TEMP = 0.0
DEFAULT_TOP_P = 1.0
DEFAULT_XTC_PROBABILITY = 0.0
DEFAULT_XTC_THRESHOLD = 0.0
DEFAULT_SEED = None
DEFAULT_MAX_TOKENS = 256
DEFAULT_MODEL = "mlx-community/Qwen3-1.7B-4bit-DWQ"


def str2bool(string):
    return string.lower() not in ["false", "f"]


def setup_arg_parser():
    """Set up and return the argument parser."""
    parser = argparse.ArgumentParser(description="Chat with an LLM")
    parser.add_argument(
        "--model",
        type=str,
        help="The path to the local model directory or Hugging Face repo.",
        default=DEFAULT_MODEL,
    )
    parser.add_argument(
        "--adapter-path",
        type=str,
        help="Optional path for the trained adapter weights and config.",
    )
    parser.add_argument(
        "--temp", type=float, default=DEFAULT_TEMP, help="Sampling temperature"
    )
    parser.add_argument(
        "--top-p", type=float, default=DEFAULT_TOP_P, help="Sampling top-p"
    )
    parser.add_argument(
        "--xtc-probability",
        type=float,
        default=DEFAULT_XTC_PROBABILITY,
        help="Probability of XTC sampling to happen each next token",
    )
    parser.add_argument(
        "--xtc-threshold",
        type=float,
        default=0.0,
        help="Thresold the probs of each next token candidate to be sampled by XTC",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="PRNG seed",
    )
    parser.add_argument(
        "--max-kv-size",
        type=int,
        help="Set the maximum key-value cache size",
        default=None,
    )
    parser.add_argument(
        "--max-tokens",
        "-m",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help="Maximum number of tokens to generate",
    )
    return parser


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()

    model, tokenizer = load(
        args.model,
        adapter_path=args.adapter_path,
        tokenizer_config={"trust_remote_code": True},
    )

    # Initialize chat history
    chat = []
    
    while True:
        try:
            user_input = input("User: ").strip()
            
            # Exit conditions
            if user_input.lower() in ['exit', 'quit', '']:
                break
            
            chat.append({"role": "user", "content": user_input})
            
            formatted_prompt = tokenizer.apply_chat_template(chat, add_generation_prompt=True)

            # Generate response
            response = ""
            print("Assistant: ", end="", flush=True)
            
            for chunk in stream_generate(
                    model,
                    tokenizer,
                    formatted_prompt,
                    max_tokens=args.max_tokens,
                    sampler=make_sampler(
                        args.temp,
                        args.top_p,
                        xtc_threshold=args.xtc_threshold,
                        xtc_probability=args.xtc_probability,
                        xtc_special_tokens=(
                            tokenizer.encode("\n") + list(tokenizer.eos_token_ids)
                        ),
                    ),
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
    print(
        "Calling `python -m mlx_lm.chat...` directly is deprecated."
        " Use `mlx_lm.chat...` or `python -m mlx_lm chat ...` instead."
    )
    main()