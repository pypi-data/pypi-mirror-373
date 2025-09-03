from typing import Generator, Optional, Any, Sequence, Union

from nexaai.common import ModelConfig, GenerationConfig, ChatMessage, PluginID
from nexaai.llm import LLM
from nexaai.mlx_backend.llm.interface import LLM as MLXLLMInterface
from nexaai.mlx_backend.ml import ModelConfig as MLXModelConfig, SamplerConfig as MLXSamplerConfig, GenerationConfig as MLXGenerationConfig, EmbeddingConfig


class MLXLLMImpl(LLM):
    def __init__(self, m_cfg: ModelConfig = ModelConfig()):
        """Initialize MLX LLM implementation."""
        super().__init__(m_cfg)
        self._mlx_llm = None

    @classmethod
    def _load_from(cls,
                   local_path: str,
                   tokenizer_path: Optional[str] = None,
                   m_cfg: ModelConfig = ModelConfig(),
                   plugin_id: Union[PluginID, str] = PluginID.MLX,
                   device_id: Optional[str] = None
        ) -> 'MLXLLMImpl':
        """Load model from local path using MLX backend."""
        try:
            # MLX interface and configs are already imported
            
            # Convert our ModelConfig to MLX ModelConfig
            mlx_config = MLXModelConfig()
            mlx_config.n_ctx = m_cfg.n_ctx
            mlx_config.n_threads = m_cfg.n_threads
            mlx_config.n_threads_batch = m_cfg.n_threads_batch
            mlx_config.n_batch = m_cfg.n_batch
            mlx_config.n_ubatch = m_cfg.n_ubatch
            mlx_config.n_seq_max = m_cfg.n_seq_max
            mlx_config.chat_template_path = m_cfg.chat_template_path
            mlx_config.chat_template_content = m_cfg.chat_template_content
            
            # Create instance and load MLX model
            instance = cls(m_cfg)
            instance._mlx_llm = MLXLLMInterface(
                model_path=local_path,
                tokenizer_path=tokenizer_path or local_path,
                config=mlx_config,
                device=device_id
            )
            
            return instance
        except Exception as e:
            raise RuntimeError(f"Failed to load MLX LLM: {str(e)}")

    def eject(self):
        """Release the model from memory."""
        if self._mlx_llm:
            self._mlx_llm.destroy()
            self._mlx_llm = None

    def apply_chat_template(
        self,
        messages: Sequence[ChatMessage], 
        tools: Optional[str] = None,
        enable_thinking: bool = True, 
        add_generation_prompt: bool = True
    ) -> str:
        """Apply the chat template to messages."""
        if not self._mlx_llm:
            raise RuntimeError("MLX LLM not loaded")
        
        try:
            # Convert to MLX ChatMessage format
            mlx_messages = []
            for msg in messages:
                # Create a simple object with role and content attributes
                class MLXChatMessage:
                    def __init__(self, role, content):
                        self.role = role
                        self.content = content
                
                # Handle both dict-style and attribute-style access
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    # Message is already an object with attributes
                    mlx_messages.append(MLXChatMessage(msg.role, msg.content))
                else:
                    # Message is a dict
                    mlx_messages.append(MLXChatMessage(msg["role"], msg["content"]))
            
            return self._mlx_llm.apply_chat_template(mlx_messages, tools=tools, enable_thinking=enable_thinking, add_generation_prompt=add_generation_prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to apply chat template: {str(e)}")

    def generate_stream(self, prompt: str, g_cfg: GenerationConfig = GenerationConfig()) -> Generator[str, None, None]:
        """Generate text with streaming."""
        if not self._mlx_llm:
            raise RuntimeError("MLX LLM not loaded")
        
        try:
            import queue
            import threading
            
            # Convert GenerationConfig to MLX format
            
            mlx_gen_config = MLXGenerationConfig()
            mlx_gen_config.max_tokens = g_cfg.max_tokens
            mlx_gen_config.stop = g_cfg.stop_words
            mlx_gen_config.image_paths = g_cfg.image_paths
            mlx_gen_config.audio_paths = g_cfg.audio_paths
            
            if g_cfg.sampler_config:
                mlx_sampler_config = MLXSamplerConfig()
                mlx_sampler_config.temperature = g_cfg.sampler_config.temperature
                mlx_sampler_config.top_p = g_cfg.sampler_config.top_p
                mlx_sampler_config.top_k = g_cfg.sampler_config.top_k
                mlx_sampler_config.repetition_penalty = g_cfg.sampler_config.repetition_penalty
                mlx_sampler_config.presence_penalty = g_cfg.sampler_config.presence_penalty
                mlx_sampler_config.frequency_penalty = g_cfg.sampler_config.frequency_penalty
                mlx_sampler_config.seed = g_cfg.sampler_config.seed
                mlx_sampler_config.grammar_path = g_cfg.sampler_config.grammar_path
                mlx_sampler_config.grammar_string = g_cfg.sampler_config.grammar_string
                mlx_gen_config.sampler_config = mlx_sampler_config
            
            # Create a queue for streaming tokens
            token_queue = queue.Queue()
            exception_container = [None]
            self.reset_cancel()  # Reset cancel flag before generation
            
            def token_callback(token: str, user_data: Any = None) -> bool:
                if self._cancel_event.is_set():
                    token_queue.put(('end', None))
                    return False
                try:
                    token_queue.put(('token', token))
                    return True
                except Exception as e:
                    exception_container[0] = e
                    return False
            
            # Run generation in a separate thread
            def generate():
                try:
                    self._mlx_llm.generate_stream(prompt, mlx_gen_config, token_callback)
                except Exception as e:
                    exception_container[0] = e
                finally:
                    token_queue.put(('end', None))
            
            thread = threading.Thread(target=generate)
            thread.start()
            
            # Yield tokens as they come from the queue
            while True:
                if exception_container[0]:
                    raise exception_container[0]
                    
                try:
                    msg_type, token = token_queue.get(timeout=0.1)
                    if msg_type == 'end':
                        break
                    elif msg_type == 'token':
                        yield token
                except queue.Empty:
                    if not thread.is_alive():
                        break
                    continue
                    
            thread.join()
            
            if exception_container[0]:
                raise exception_container[0]
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate streaming text: {str(e)}")

    def generate(self, prompt: str, g_cfg: GenerationConfig = GenerationConfig()) -> str:
        """
        Generate text without streaming.

        Args:
            prompt (str): The prompt to generate text from.
            g_cfg (GenerationConfig): Generation configuration.

        Returns:
            str: The generated text.
        """
        if not self._mlx_llm:
            raise RuntimeError("MLX LLM not loaded")
        
        try:
            # Convert GenerationConfig to MLX format
            
            mlx_gen_config = MLXGenerationConfig()
            mlx_gen_config.max_tokens = g_cfg.max_tokens
            mlx_gen_config.stop = g_cfg.stop_words
            mlx_gen_config.image_paths = g_cfg.image_paths
            mlx_gen_config.audio_paths = g_cfg.audio_paths
            
            if g_cfg.sampler_config:
                mlx_sampler_config = MLXSamplerConfig()
                mlx_sampler_config.temperature = g_cfg.sampler_config.temperature
                mlx_sampler_config.top_p = g_cfg.sampler_config.top_p
                mlx_sampler_config.top_k = g_cfg.sampler_config.top_k
                mlx_sampler_config.repetition_penalty = g_cfg.sampler_config.repetition_penalty
                mlx_sampler_config.presence_penalty = g_cfg.sampler_config.presence_penalty
                mlx_sampler_config.frequency_penalty = g_cfg.sampler_config.frequency_penalty
                mlx_sampler_config.seed = g_cfg.sampler_config.seed
                mlx_sampler_config.grammar_path = g_cfg.sampler_config.grammar_path
                mlx_sampler_config.grammar_string = g_cfg.sampler_config.grammar_string
                mlx_gen_config.sampler_config = mlx_sampler_config
            
            # Simple token callback that just continues
            def token_callback(token: str, user_data: Any = None) -> bool:
                return not self._cancel_event.is_set()
            
            # Use MLX streaming generation and return the full result
            return self._mlx_llm.generate_stream(prompt, mlx_gen_config, token_callback)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {str(e)}")

    def save_kv_cache(self, path: str):
        """
        Save the key-value cache to the file.

        Args:
            path (str): The path to the file.
        """
        if not self._mlx_llm:
            raise RuntimeError("MLX LLM not loaded")
        
        try:
            success = self._mlx_llm.save_kv_cache(path)
            if not success:
                raise RuntimeError("Failed to save KV cache")
        except Exception as e:
            raise RuntimeError(f"Failed to save KV cache: {str(e)}")

    def load_kv_cache(self, path: str):
        """
        Load the key-value cache from the file.

        Args:
            path (str): The path to the file.
        """
        if not self._mlx_llm:
            raise RuntimeError("MLX LLM not loaded")
        
        try:
            success = self._mlx_llm.load_kv_cache(path)
            if not success:
                raise RuntimeError("Failed to load KV cache")
        except Exception as e:
            raise RuntimeError(f"Failed to load KV cache: {str(e)}")

    def reset(self):
        """
        Reset the LLM model context and KV cache.
        """
        if not self._mlx_llm:
            raise RuntimeError("MLX LLM not loaded")
        
        try:
            self._mlx_llm.reset()
        except Exception as e:
            raise RuntimeError(f"Failed to reset MLX LLM: {str(e)}")
