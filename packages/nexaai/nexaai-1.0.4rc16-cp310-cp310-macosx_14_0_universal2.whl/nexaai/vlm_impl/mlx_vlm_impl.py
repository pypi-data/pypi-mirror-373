from typing import Generator, Optional, List, Dict, Any, Union

from nexaai.common import ModelConfig, GenerationConfig, MultiModalMessage, PluginID
from nexaai.vlm import VLM
from nexaai.mlx_backend.vlm.interface import VLM as MLXVLMInterface
from nexaai.mlx_backend.ml import ModelConfig as MLXModelConfig, SamplerConfig as MLXSamplerConfig, GenerationConfig as MLXGenerationConfig, EmbeddingConfig


class MlxVlmImpl(VLM):
    def __init__(self, m_cfg: ModelConfig = ModelConfig()):
        """Initialize MLX VLM implementation."""
        super().__init__(m_cfg)
        self._mlx_vlm = None

    @classmethod
    def _load_from(cls,
                   local_path: str,
                   mmproj_path: str,
                   m_cfg: ModelConfig = ModelConfig(),
                   plugin_id: Union[PluginID, str] = PluginID.MLX,
                   device_id: Optional[str] = None
        ) -> 'MlxVlmImpl':
        """Load VLM model from local path using MLX backend.
        
        Args:
            local_path: Path to the main model file
            mmproj_path: Path to the multimodal projection file (not used in MLX VLM)
            m_cfg: Model configuration
            plugin_id: Plugin identifier
            device_id: Optional device ID
            
        Returns:
            MlxVlmImpl instance
        """
        try:
            # MLX interface is already imported
            
            # Create instance and load MLX VLM
            instance = cls(m_cfg)
            instance._mlx_vlm = MLXVLMInterface(
                model_path=local_path,
                mmproj_path=mmproj_path,  # MLX VLM may not use this, but pass it anyway
                context_length=m_cfg.n_ctx,
                device=device_id
            )
            
            return instance
        except Exception as e:
            raise RuntimeError(f"Failed to load MLX VLM: {str(e)}")

    def eject(self):
        """Release the model from memory."""
        if self._mlx_vlm:
            self._mlx_vlm.destroy()
            self._mlx_vlm = None

    def reset(self):
        """
        Reset the VLM model context and KV cache.
        """
        if not self._mlx_vlm:
            raise RuntimeError("MLX VLM not loaded")
        
        try:
            self._mlx_vlm.reset()
        except Exception as e:
            raise RuntimeError(f"Failed to reset MLX VLM: {str(e)}")

    def apply_chat_template(
        self,
        messages: List[MultiModalMessage],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Apply the chat template to multimodal messages."""
        if not self._mlx_vlm:
            raise RuntimeError("MLX VLM not loaded")
        
        try:
            mlx_messages = []
            total_images = 0
            total_audios = 0
            
            for msg in messages:
                # Create a simple object with role and content attributes
                class MLXChatMessage:
                    def __init__(self, role, content):
                        self.role = role
                        self.content = content
                
                # Extract text content and count media files
                text_content = ""
                first_content = True
                
                for content_item in msg["content"]:
                    content_type = content_item.get("type", "")
                    
                    if content_type == "text":
                        if not first_content:
                            text_content += " "
                        text_content += content_item.get("text", "")
                        first_content = False
                    elif content_type == "image":
                        total_images += 1
                    elif content_type == "audio":
                        total_audios += 1
                
                mlx_messages.append(MLXChatMessage(msg["role"], text_content))
            
            if total_images > 0 or total_audios > 0:
                # Use apply_chat_template_with_media when media is present
                return self._mlx_vlm.apply_chat_template_with_media(
                    mlx_messages,
                    num_images=total_images,
                    num_audios=total_audios,
                    tools=tools,
                    enable_thinking=False  # Default to False, could be made configurable
                )
            else:
                # Use regular apply_chat_template for text-only messages
                return self._mlx_vlm.apply_chat_template(mlx_messages)
                
        except Exception as e:
            raise RuntimeError(f"Failed to apply chat template: {str(e)}")

    def generate_stream(self, prompt: str, g_cfg: GenerationConfig = GenerationConfig()) -> Generator[str, None, None]:
        """Generate text with streaming."""
        if not self._mlx_vlm:
            raise RuntimeError("MLX VLM not loaded")
        
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
            
            import queue
            import threading
            
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
                    self._mlx_vlm.generate_stream(prompt, mlx_gen_config, token_callback)
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
        if not self._mlx_vlm:
            raise RuntimeError("MLX VLM not loaded")
        
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
            return self._mlx_vlm.generate_stream(prompt, mlx_gen_config, token_callback)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {str(e)}")
