from typing import List, Union
import numpy as np

from nexaai.common import PluginID
from nexaai.embedder import Embedder, EmbeddingConfig
from nexaai.mlx_backend.embedding.interface import Embedder as MLXEmbedderInterface
from nexaai.mlx_backend.ml import ModelConfig as MLXModelConfig, SamplerConfig as MLXSamplerConfig, GenerationConfig as MLXGenerationConfig, EmbeddingConfig


class MLXEmbedderImpl(Embedder):
    def __init__(self):
        """Initialize MLX Embedder implementation."""
        super().__init__()
        self._mlx_embedder = None

    @classmethod
    def _load_from(cls, model_path: str, tokenizer_file: str = "tokenizer.json", plugin_id: Union[PluginID, str] = PluginID.MLX):
        """
        Load an embedder from model files using MLX backend.

        Args:
            model_path: Path to the model file
            tokenizer_file: Path to the tokenizer file (default: "tokenizer.json")
            plugin_id: Plugin ID to use for the model (default: PluginID.MLX)

        Returns:
            MLXEmbedderImpl instance
        """
        try:
            # MLX interface is already imported
            
            # Create instance and load MLX embedder
            instance = cls()
            instance._mlx_embedder = MLXEmbedderInterface(
                model_path=model_path,
                tokenizer_path=tokenizer_file
            )
            
            # Load the model
            success = instance._mlx_embedder.load_model(model_path)
            if not success:
                raise RuntimeError("Failed to load MLX embedder model")
            
            return instance
        except Exception as e:
            raise RuntimeError(f"Failed to load MLX Embedder: {str(e)}")

    def eject(self):
        """
        Clean up resources and destroy the embedder
        """
        if self._mlx_embedder:
            self._mlx_embedder.destroy()
            self._mlx_embedder = None

    def generate(self, texts: Union[List[str], str] = None, config: EmbeddingConfig = EmbeddingConfig(), input_ids: Union[List[int], List[List[int]]] = None) -> np.ndarray:
        """
        Generate embeddings for the given texts or input_ids.

        Args:
            texts: List of strings or single string to embed
            input_ids: Pre-tokenized input as:
                      - Single sequence: list of integers [1, 2, 3, 4]
                      - Multiple sequences: list of lists [[1, 2, 3], [4, 5, 6]]
            config: Configuration for embedding generation

        Returns:
            numpy array of embeddings with shape (num_sequences, embedding_dim)
        """
        if not self._mlx_embedder:
            raise RuntimeError("MLX Embedder not loaded")
        
        if texts is None and input_ids is None:
            raise ValueError("Either texts or input_ids must be provided")
        
        # MLX embedder currently only supports text input, not pre-tokenized input_ids
        if input_ids is not None:
            raise NotImplementedError("MLX embedder does not support input_ids, only text input")
        
        try:
            # Convert single string to list if needed
            if isinstance(texts, str):
                texts = [texts]
            
            # MLX config classes are already imported
            
            # Convert our config to MLX config
            mlx_config = EmbeddingConfig()
            mlx_config.batch_size = config.batch_size
            mlx_config.normalize = config.normalize
            mlx_config.normalize_method = config.normalize_method
            
            # Generate embeddings using MLX
            embeddings = self._mlx_embedder.embed(texts, mlx_config)
            
            # Convert to numpy array
            return np.array(embeddings, dtype=np.float32)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")

    def get_embedding_dim(self) -> int:
        """
        Get the embedding dimension of the model

        Returns:
            The embedding dimension in int
        """
        if not self._mlx_embedder:
            raise RuntimeError("MLX Embedder not loaded")
        
        try:
            return self._mlx_embedder.embedding_dim()
        except Exception as e:
            raise RuntimeError(f"Failed to get embedding dimension: {str(e)}")
