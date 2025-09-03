from __future__ import annotations

import json
import os
from typing import Any, List, Optional, Sequence, Tuple, Union
import mlx.core as mx
import os
import time

# Import necessary modules from mlx_lm
from mlx_lm import generate, stream_generate, load
from mlx_lm.sample_utils import make_sampler, make_logits_processors
from mlx_lm.models.cache import make_prompt_cache, save_prompt_cache, load_prompt_cache
from mlx_lm.tokenizer_utils import TokenizerWrapper
from mlx_lm.generate import generate_step
from mlx_lm.tuner.utils import load_adapters
import mlx.core as mx

# Import configs and callback types from ml.py for API alignment
from ml import (
    LLM as BaseLLM,
    ModelConfig,
    SamplerConfig,
    GenerationConfig,
    ChatMessage,
    EmbeddingConfig,
    TokenCallback,
    Path,
    Tool
)

# Import profiling module
from profiling import ProfilingMixin, ProfilingData, StopReason

class LLM(BaseLLM, ProfilingMixin):
    """
    LLM interface for mlx-lm.
    API aligned with ml.py LLM abstract base class.
    """

    def __init__(
        self,
        model_path: Path,
        tokenizer_path: Path,
        config: ModelConfig,
        device: Optional[str] = None,
    ) -> None:
        """
        Initialize the LLM model.
        """
        # Initialize profiling mixin
        ProfilingMixin.__init__(self)

        # Check if model_path is a file, if so use its parent directory, since MLX requires loading from a directory
        if os.path.isfile(model_path):
            model_path = os.path.dirname(model_path)

        # Call parent constructor
        super().__init__(model_path, tokenizer_path, config, device)

        # For MLX, we ignore ModelConfig parameters as requested
        # Store the basic parameters
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.config = config  # Store but ignore the values
        self.device = device if device is not None else "cpu"

        # Simulate C handle (would be pointer in C, here just store info)
        self.handle = {
            "model_path": model_path,
            "tokenizer_path": tokenizer_path,
            "device": self.device,
        }

        # Load model and tokenizer using mlx-lm
        self.model, self.tokenizer = load(model_path)
        self.sampler_config = SamplerConfig()
        self.default_generation_config = GenerationConfig()
        self.kv_cache = None
        # Initialize cache and global tracking (similar to reset logic)
        self._reset_cache()
        self.token_generator = None
        self.loras = {}
        self.current_lora_id = -1
        self._next_lora_id = 0
        # Track whether KV cache has been used for generation
        self.kv_cache_used = False
        # Track total tokens processed (prompts + responses) for prompt cache functionality
        self.global_n_past = 0

    def destroy(self) -> None:
        """Destroy LLM instance and free associated resources (ml_llm_destroy)."""
        self.model = None
        self.tokenizer = None
        self.kv_cache = None
        self.token_generator = None
        self.sampler_config = SamplerConfig()
        self.default_generation_config = GenerationConfig()
        self.loras.clear()
        self.current_lora_id = -1
        self._next_lora_id = 0
        self.kv_cache_used = False
        self.global_n_past = 0
        self.reset_profiling()

    def reset(self) -> None:
        """Reset LLM internal state (ml_llm_reset)."""
        mx.clear_cache()
        self._reset_cache()
        self.reset_profiling()

    def _reset_cache(self) -> None:
        """Reset the KV cache."""
        if self.model is not None:
            # For MLX, let mlx-lm handle cache size automatically since we ignore ModelConfig
            # Use n_ctx if provided and > 0, otherwise let mlx-lm decide
            max_kv_size = self.config.n_ctx if self.config.n_ctx > 0 else None
            if max_kv_size:
                self.kv_cache = make_prompt_cache(self.model, max_kv_size=max_kv_size)
            else:
                self.kv_cache = make_prompt_cache(self.model)
            self.token_generator = None  # Reset generator for new conversation
            self.kv_cache_used = False  # Reset cache usage flag
            self.global_n_past = 0  # Reset prompt cache tracking

    # Tokenization methods
    def encode(self, text: str) -> List[int]:
        """Encode UTF-8 text to token IDs (ml_llm_encode)."""
        if not isinstance(self.tokenizer, TokenizerWrapper):
            wrapper = TokenizerWrapper(self.tokenizer)
            return wrapper.encode(text, add_special_tokens=True)
        return self.tokenizer.encode(text, add_special_tokens=True)

    def decode(self, token_ids: Sequence[int]) -> str:
        """Decode token IDs to UTF-8 text (ml_llm_decode)."""
        if not isinstance(self.tokenizer, TokenizerWrapper):
            wrapper = TokenizerWrapper(self.tokenizer)
            return wrapper.decode(list(token_ids))
        return self.tokenizer.decode(list(token_ids))

    # KV-cache methods
    def save_kv_cache(self, path: Path) -> bool:
        """Save KV cache to file. Returns True on success, False on error."""
        try:
            if self.kv_cache is not None:
                if not path.endswith('.safetensors'):
                    path = path + '.safetensors'
                save_prompt_cache(path, self.kv_cache)
                return True
            return False
        except Exception as e:
            print(f"Error saving KV cache: {e}")
            return False

    def load_kv_cache(self, path: Path) -> bool:
        """Load KV cache from file. Returns True on success, False on error."""
        try:
            if not path.endswith('.safetensors'):
                path = path + '.safetensors'
            self.kv_cache = load_prompt_cache(path)
            return True
        except Exception as e:
            print(f"Error loading KV cache: {e}")
            return False

    # LoRA methods
    #
    # LoRA (Low-Rank Adaptation) support for fine-tuned model variants.
    # This implementation supports dynamic switching between different LoRA adapters
    # by reloading the model with the appropriate adapter weights.
    #
    # Usage:
    # 1. Add LoRA adapter: lora_id = model.add_lora("/path/to/adapter")
    # 2. Activate LoRA: model.set_lora(lora_id)
    # 3. Switch back to base model: model.set_lora(-1)
    # 4. Or combine steps 1-2: lora_id = model.load_and_activate_lora("/path/to/adapter")

    def set_lora(self, lora_id: int) -> None:
        """Set active LoRA adapter by ID (ml_llm_set_lora)."""
        if lora_id == -1:
            if self.current_lora_id != -1:
                self._switch_to_base_model()
            return
        if lora_id not in self.loras:
            raise ValueError(f"LoRA adapter with ID {lora_id} not found")
        if self.current_lora_id != lora_id:
            self._switch_to_lora(lora_id)

    def add_lora(self, lora_path: Path) -> int:
        """Add LoRA adapter from file (ml_llm_add_lora). Returns LoRA ID on success, negative on error."""
        if not lora_path or not os.path.exists(lora_path):
            return -1
        if not self._validate_lora_adapter(lora_path):
            return -2
        for lora_id, (path, _) in self.loras.items():
            if os.path.abspath(path) == os.path.abspath(lora_path):
                return lora_id
        lora_id = self._next_lora_id
        self._next_lora_id += 1
        try:
            adapters = load_adapters(lora_path)
            self.loras[lora_id] = (lora_path, adapters)
            return lora_id
        except Exception:
            return -99

    def _validate_lora_adapter(self, lora_path: Path) -> bool:
        """Validate that a path contains a valid LoRA adapter."""
        if not os.path.isdir(lora_path):
            return False

        # Check for required LoRA files
        required_files = ["adapter_config.json"]
        optional_files = [
            "adapters.safetensors",
            "adapter_model.safetensors",
            "pytorch_model.bin",  # PyTorch format
            "adapter_model.bin",   # Alternative PyTorch format
        ]

        # At least adapter_config.json should exist
        config_exists = any(os.path.exists(os.path.join(lora_path, f)) for f in required_files)
        if not config_exists:
            return False

        # At least one weight file should exist
        weights_exist = any(os.path.exists(os.path.join(lora_path, f)) for f in optional_files)

        return weights_exist

    def remove_lora(self, lora_id: int) -> None:
        """Remove LoRA adapter by ID (ml_llm_remove_lora)."""
        if lora_id not in self.loras:
            return
        if self.current_lora_id == lora_id:
            self._switch_to_base_model()
        self.loras.pop(lora_id, None)

    def list_loras(self) -> List[int]:
        """List all loaded LoRA adapter IDs (ml_llm_list_loras)."""
        return list(self.loras.keys())

    def _switch_to_base_model(self) -> None:
        """Switch to the base model (no LoRA)."""
        try:
            # Reload the base model
            self.model, self.tokenizer = load(self.model_path)
            self.current_lora_id = -1
            self._reset_cache()  # Reset cache when switching models
        except Exception as e:
            raise RuntimeError(f"Failed to switch to base model: {str(e)}")

    def _switch_to_lora(self, lora_id: int) -> None:
        """Switch to a specific LoRA adapter."""
        if lora_id not in self.loras:
            raise ValueError(f"LoRA adapter with ID {lora_id} not found")

        try:
            lora_path, adapters = self.loras[lora_id]

            # Load model with LoRA adapter
            self.model, self.tokenizer = load(self.model_path, adapter_path=lora_path)
            self.current_lora_id = lora_id
            self._reset_cache()  # Reset cache when switching models
        except Exception as e:
            raise RuntimeError(f"Failed to switch to LoRA adapter {lora_id} (path: {lora_path}): {str(e)}")

    def get_current_lora_id(self) -> int:
        """Get the currently active LoRA adapter ID."""
        return self.current_lora_id

    def get_lora_info(self, lora_id: int) -> dict:
        """Get information about a specific LoRA adapter."""
        if lora_id not in self.loras:
            raise ValueError(f"LoRA adapter with ID {lora_id} not found")

        lora_path, adapters = self.loras[lora_id]
        return {
            "id": lora_id,
            "path": lora_path,
            "is_active": lora_id == self.current_lora_id,
            "config": getattr(adapters, "config", None) if hasattr(adapters, "config") else None
        }

    def load_and_activate_lora(self, lora_path: Path) -> int:
        """Load a LoRA adapter and immediately activate it."""
        lora_id = self.add_lora(lora_path)
        self.set_lora(lora_id)
        return lora_id

    # Sampler methods
    def set_sampler(self, config: SamplerConfig) -> None:
        """Configure text generation sampling parameters (ml_llm_set_sampler)."""
        self.sampler_config = config

    def reset_sampler(self) -> None:
        """Reset sampling parameters to defaults (ml_llm_reset_sampler)."""
        self.sampler_config = SamplerConfig()

    # Generation config methods
    def set_generation_config(self, config: GenerationConfig) -> None:
        """Set default generation configuration for token-level generation."""
        self.default_generation_config = config

    def _make_mlx_sampler_from_config(self, sampler_config: SamplerConfig):
        """Create mlx-lm sampler from specific config."""
        # Set seed if specified
        if sampler_config.seed != -1:
            mx.random.seed(sampler_config.seed)

        return make_sampler(
            temp=sampler_config.temperature,
            top_p=sampler_config.top_p,
            top_k=sampler_config.top_k,
        )

    def _make_logits_processors_from_config(self, sampler_config: SamplerConfig):
        """Create logits processors from specific config."""
        # Only use repetition penalty which is natively supported by mlx-lm
        if sampler_config.repetition_penalty != 1.0:
            return make_logits_processors(
                repetition_penalty=sampler_config.repetition_penalty,
            )
        return None

    def _make_mlx_sampler(self):
        """Create mlx-lm sampler from class config."""
        return self._make_mlx_sampler_from_config(self.sampler_config)

    def _make_logits_processors(self):
        """Create logits processors from class config."""
        return self._make_logits_processors_from_config(self.sampler_config)

    def generate_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig],
        on_token: TokenCallback,
        user_data: Any = None,
    ) -> str:
        """
        Generate text with streaming callback and profiling.

        The prompt should be the incremental part after applying chat template.
        apply_chat_template now returns only the incremental prompt based on global_n_past:
        - First round (global_n_past = 0): Last user message + last system message (if exists)
        - Subsequent rounds (global_n_past > 0): Only last user message
        
        Prompt Cache Behavior:
        - Tracks global_n_past to know how many tokens (prompts + responses) have been processed
        - Passes incremental token arrays directly to stream_generate as prompt cache already contains the past history
        - KV cache retains the conversation context until reset() is called
        """
        # Start profiling
        self._start_profiling()

        if config is None:
            config = GenerationConfig()

        # Use sampler config from GenerationConfig if provided, otherwise use class config
        effective_sampler_config = config.sampler_config if config.sampler_config else self.sampler_config

        # Create sampler from effective config
        sampler = self._make_mlx_sampler_from_config(effective_sampler_config)
        logits_processors = self._make_logits_processors_from_config(effective_sampler_config)

        is_first_round = self.global_n_past <= 0
        
        # Encode prompt to get tokens
        incremental_tokens = self.encode(prompt)
        cached_tokens = 0

        # Only offset prefix kv-cache at first round
        if is_first_round:
        
            # Handle KV cache prefix offset if available
            if self.kv_cache is not None and len(self.kv_cache) > 0:
                # Get the offset from the first cache layer
                if hasattr(self.kv_cache[0], 'offset'):
                    cached_tokens = self.kv_cache[0].offset - 1
            
            # Process only the non-cached tokens
            incremental_tokens = incremental_tokens[cached_tokens:] if cached_tokens > 0 else incremental_tokens
            
            if len(incremental_tokens) == 0:
                raise ValueError("No tokens to process, KV cache is too long.")
            
        # Since apply_chat_template now returns incremental prompts, we can use the prompt directly
        # The prompt is already the incremental part based on global_n_past
        incremental_length = len(incremental_tokens)
        
        # Record prompt tokens for profiling (use incremental length for this call)
        self._update_prompt_tokens(incremental_length)

        generated_tokens = 0
        full_text = ""
        last_response = None
        first_token = True

        try:
            # End prompt processing, start decode
            self._prompt_end()
            self._decode_start()

            for response in stream_generate(
                model=self.model,
                tokenizer=self.tokenizer,
                prompt=incremental_tokens,
                max_tokens=config.max_tokens,
                sampler=sampler,
                logits_processors=logits_processors if logits_processors else None,
                prompt_cache=self.kv_cache,
            ):
                # Record TTFT on first token
                if first_token:
                    self._record_ttft()
                    first_token = False

                token_text = response.text
                generated_tokens += 1

                # Call the token callback - if it returns False, stop generation
                if not on_token(token_text, user_data):
                    self._set_stop_reason(StopReason.ML_STOP_REASON_USER)
                    break
                full_text += token_text
                last_response = response

            # Set stop reason based on how generation ended
            if generated_tokens >= config.max_tokens:
                self._set_stop_reason(StopReason.ML_STOP_REASON_LENGTH)
            elif self._profiling_context.stop_reason != StopReason.ML_STOP_REASON_USER:  # Don't override user stop
                # Check if the last response indicates EOS stop
                if last_response:
                    if hasattr(last_response, 'finish_reason') and last_response.finish_reason == "stop":
                        self._set_stop_reason(StopReason.ML_STOP_REASON_EOS)
                    else:
                        self._set_stop_reason(StopReason.ML_STOP_REASON_COMPLETED)
                else:
                    # Fallback: generation loop ended naturally, likely due to EOS
                    self._set_stop_reason(StopReason.ML_STOP_REASON_EOS)

            # Update global_n_past to reflect the new tokens processed (incremental prompt + response)
            # Use the response metadata to get accurate token counts
            self.global_n_past += cached_tokens + incremental_length + last_response.generation_tokens

            # Mark cache as used after successful generation
            self.kv_cache_used = True

            # Update generated tokens and end profiling
            self._update_generated_tokens(generated_tokens)
            self._decode_end()
            self._end_profiling()

            return full_text
        except Exception as e:
            import traceback
            self._set_stop_reason(StopReason.ML_STOP_REASON_UNKNOWN)
            self._decode_end()
            self._end_profiling()
            return f"Streaming generation error: {str(e)}\n{traceback.format_exc()}"

    # Chat template methods
    def get_chat_template(self, template_name: str) -> str:
        """Get chat template by name."""
        # The header expects a template_name argument, but mlx-lm only supports one template.
        # We'll ignore the argument for now.
        return self.tokenizer.chat_template

    def apply_chat_template(self, messages: Sequence[ChatMessage], tools: Optional[str] = None, enable_thinking: bool = True, add_generation_prompt: bool = True) -> str:
        """
        Apply chat template to messages with incremental prompt support and optional tools.
        
        This method now returns only the incremental prompt based on global_n_past:
        - When global_n_past = 0 (first conversation): Last user message + last system message (if exists)
        - When global_n_past > 0 (subsequent rounds): Only last user message
        """
        # TODO: this is temporary solution to account for the no-thinking requirement of GPT-OSS. In the long term we need to revisit the API design of apply_chat_template.
        try:
            # Check global_n_past > 0 to determine if this is the first round of conversation
            is_first_round = self.global_n_past <= 0
            
            # Find last user message and last system message
            last_user_msg = None
            last_system_msg = None
            
            for msg in messages:
                if msg.role == "user":
                    last_user_msg = msg
                elif msg.role == "system":
                    last_system_msg = msg
            
            # Build incremental message list based on conversation round
            if is_first_round:
                # First round: include system message (if exists) + last user message
                incremental_messages = []
                if last_system_msg:
                    incremental_messages.append({
                        "role": last_system_msg.role,
                        "content": last_system_msg.content
                    })
                
                if last_user_msg:
                    incremental_messages.append({
                        "role": last_user_msg.role,
                        "content": last_user_msg.content
                    })
                else:
                    raise ValueError("No user message found for first conversation round")
                    
            else:
                # Subsequent rounds: only last user message
                if last_user_msg:
                    incremental_messages = [{
                        "role": last_user_msg.role,
                        "content": last_user_msg.content
                    }]
                else:
                    raise ValueError("No user message found for subsequent conversation round")
            
            parsed_tools = None
            if tools is not None:
                parsed_tools = json.loads(tools)

            return self.tokenizer.apply_chat_template(
                incremental_messages,
                tokenize=False,
                enable_thinking=enable_thinking,   
                add_generation_prompt=add_generation_prompt,
                tools=parsed_tools
            )
        except Exception as e:
            import traceback
            raise RuntimeError(f"Error applying chat template: {str(e)}\n{traceback.format_exc()}")

    # Embeddings - using the model's embedding layer directly
    def embed(
        self,
        texts: Sequence[str],
        config: Optional[EmbeddingConfig] = None,
    ) -> List[List[float]]:
        """Generate embeddings for texts with profiling."""
        # Start profiling
        self._start_profiling()

        # Calculate total tokens for all texts
        total_tokens = sum(len(self.encode(text)) for text in texts)
        self._update_prompt_tokens(total_tokens)

        # End prompt processing, start decode
        self._prompt_end()
        self._decode_start()

        try:
            embeddings = []

            for text in texts:
                # Tokenize the text
                tokens = self.encode(text)

                # Convert to mlx array
                token_array = mx.array(tokens)

                # Get embeddings directly from the model's embedding layer
                embedding_tensor = self.model.model.embed_tokens(token_array)

                # Average pool across sequence dimension to get a single embedding per text
                # Shape: [seq_len, hidden_size] -> [hidden_size]
                pooled_embedding = mx.mean(embedding_tensor, axis=0)

                # Convert to Python list of floats
                embedding_list = pooled_embedding.tolist()
                embeddings.append(embedding_list)

            # End timing and finalize profiling data
            self._update_generated_tokens(0)  # No generation in embedding
            self._set_stop_reason(StopReason.ML_STOP_REASON_COMPLETED)
            self._decode_end()
            self._end_profiling()

            return embeddings

        except Exception as e:
            self._set_stop_reason(StopReason.ML_STOP_REASON_UNKNOWN)
            self._decode_end()
            self._end_profiling()
            raise RuntimeError(f"Error generating embeddings: {str(e)}")

# =============================================================================
# Test functions
# =============================================================================
# Add test functions at the bottom before the main conversation test
def test_kv_cache_save_load():
    """Test KV cache save and load functionality"""
    print("Testing KV cache save and load...")

    # Initialize model
    model_path = "mlx-community/Qwen3-1.7B-4bit-DWQ"
    config = ModelConfig()
    config.n_ctx = 512

    llm = LLM(model_path, model_path, config)

    def stream_callback(token, user_data):
        print(token, end="", flush=True)
        return True

    # Test prompt
    test_prompt = "🥳 🎂 Once upon a time"

    # Test save
    print("Testing KV cache save...")
    gen_config = GenerationConfig()
    gen_config.max_tokens = 20  # Generate enough tokens to populate cache

    print("Generating text to populate cache:")
    response = llm.generate_stream(test_prompt, gen_config, stream_callback)
    print(f"\nGenerated: {response}")

    cache_path = "./test_kvcache_save.safetensors"
    save_result = llm.save_kv_cache(cache_path)
    print(f"Save result: {save_result}")
    assert save_result == True, "KV cache save should succeed"

    # Reset cache
    llm.reset()

    # Test load
    print("Testing KV cache load...")
    cache_path = "./test_kvcache_load.safetensors"

    # First generate and save
    response = llm.generate_stream(test_prompt, gen_config, stream_callback)
    save_result = llm.save_kv_cache(cache_path)
    assert save_result == True, "KV cache save should succeed"

    # Reset and load
    llm.reset()
    load_result = llm.load_kv_cache(cache_path)
    print(f"Load result: {load_result}")
    assert load_result == True, "KV cache load should succeed"

    print("KV cache save/load tests passed!")

def test_tokenization():
    """Test encode and decode functionality"""
    print("Testing tokenization...")

    model_path = "mlx-community/Qwen3-1.7B-4bit-DWQ"
    config = ModelConfig()

    llm = LLM(model_path, model_path, config)

    test_text = "🥳 🎂 Once upon a time"

    # Test encode
    token_ids = llm.encode(test_text)
    print(f"Encoded '{test_text}' to {len(token_ids)} tokens")
    assert len(token_ids) > 0, "Encoding should produce tokens"

    # Test decode
    decoded_text = llm.decode(token_ids)
    print(f"Decoded back to: '{decoded_text}'")
    assert len(decoded_text) > 0, "Decoding should produce text"

    print("Tokenization tests passed!")

def test_generation():
    """Test basic text generation"""
    print("Testing generation...")

    model_path = "mlx-community/Qwen3-1.7B-4bit-DWQ"
    config = ModelConfig()

    llm = LLM(model_path, model_path, config)

    def stream_callback(token, user_data):
        print(token, end="", flush=True)
        return True

    test_prompt = "🥳 🎂 Once upon a time"
    gen_config = GenerationConfig()
    gen_config.max_tokens = 10

    print("Generating text:")
    response = llm.generate_stream(test_prompt, gen_config, stream_callback)
    print(f"\nGenerated response length: {len(response)}")
    assert len(response) > 0, "Generation should produce text"

    print("Generation test passed!")

def run_tests():
    """Run all test cases"""
    try:
        test_tokenization()
        print()
        test_generation()
        print()
        test_kv_cache_save_load()
        print()
        print("All tests passed! ✅")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

# For testing
if __name__ == "__main__":
    import sys

    # Check if running tests
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_tests()
        sys.exit(0)

    def on_token(token_text, user_data):
        """Token callback that prints each token as it's generated"""
        print(token_text, end="", flush=True)
        return True  # Continue generation

    # Multi-round conversation test case
    model_path = "mlx-community/Qwen3-1.7B-4bit-DWQ"
    tokenizer_path = "mlx-community/Qwen3-1.7B-4bit-DWQ"
    config = ModelConfig()

    llm = LLM(model_path, tokenizer_path, config)

    # Run tests
    print("================================================")
    print("Running tests")
    run_tests()
    print("================================================")

    # Multi-round conversation test case
    chat = []
    print("Multi-round conversation test. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("User: ").strip()

            # Exit conditions
            if user_input.lower() in ['exit', 'quit', '']:
                break

            # Add user message to chat history
            chat.append(ChatMessage(role="user", content=user_input))

            # Apply chat template to get full conversation history as formatted prompt
            formatted_prompt = llm.apply_chat_template(chat)
            # Generate response using streaming with on_token callback
            print("Assistant: ", end="", flush=True)  # Following generate.py pattern
            response = llm.generate_stream(formatted_prompt, None, on_token)

            # Add assistant response to chat history for next round
            chat.append(ChatMessage(role="assistant", content=response))
            print()  # New line after response

        except KeyboardInterrupt:
            print("\nConversation interrupted by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
