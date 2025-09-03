from typing import List, Union
from dataclasses import dataclass
from abc import abstractmethod
import numpy as np

from nexaai.base import BaseModel
from nexaai.common import PluginID


@dataclass
class EmbeddingConfig:
    batch_size: int = 32
    normalize: bool = True
    normalize_method: str = "l2"


class Embedder(BaseModel):
    def __init__(self):
        """
        Internal initializer
        """
        pass

    @classmethod
    def _load_from(cls, model_path: str, tokenizer_file: str = "tokenizer.json", plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP):
        """
        Load an embedder from model files, routing to appropriate implementation.

        Args:
            model_path: Path to the model file
            tokenizer_file: Path to the tokenizer file (default: "tokenizer.json")
            plugin_id: Plugin ID to use for the model (default: PluginID.LLAMA_CPP)

        Returns:
            Embedder instance
        """
        # Check plugin_id value for routing - handle both enum and string
        plugin_value = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        if plugin_value == "mlx":
            from nexaai.embedder_impl.mlx_embedder_impl import MLXEmbedderImpl
            return MLXEmbedderImpl._load_from(model_path, tokenizer_file, plugin_id)
        else:
            from nexaai.embedder_impl.pybind_embedder_impl import PyBindEmbedderImpl
            return PyBindEmbedderImpl._load_from(model_path, tokenizer_file, plugin_id)

    @abstractmethod
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
        pass

    @abstractmethod
    def get_embedding_dim(self) -> int:
        """
        Get the embedding dimension of the model

        Returns:
            The embedding dimension in int
        """
        pass
