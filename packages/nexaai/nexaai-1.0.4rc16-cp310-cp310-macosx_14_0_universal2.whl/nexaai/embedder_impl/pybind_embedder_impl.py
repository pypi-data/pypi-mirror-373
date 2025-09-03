from typing import List, Union
import numpy as np

from nexaai.common import PluginID
from nexaai.embedder import Embedder, EmbeddingConfig
from nexaai.binds import embedder_bind
from nexaai.runtime import _ensure_runtime


class PyBindEmbedderImpl(Embedder):
    def __init__(self, _handle_ptr):
        """
        Internal initializer
        """
        super().__init__()
        self._handle = _handle_ptr

    @classmethod
    def _load_from(cls, model_path: str, tokenizer_file: str = "tokenizer.json", plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP):
        """
        Load an embedder from model files

        Args:
            model_path: Path to the model file
            tokenizer_file: Path to the tokenizer file (default: "tokenizer.json")
            plugin_id: Plugin ID to use for the model (default: PluginID.LLAMA_CPP)

        Returns:
            PyBindEmbedderImpl instance
        """
        _ensure_runtime()
        # Convert enum to string for C++ binding
        plugin_id_str = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        handle = embedder_bind.ml_embedder_create(model_path, tokenizer_file, plugin_id_str)
        return cls(handle)

    def eject(self):
        """
        Clean up resources and destroy the embedder
        """
        # Destructor of the handle will unload the model correctly
        del self._handle
        self._handle = None

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
        if texts is None and input_ids is None:
            raise ValueError("Either texts or input_ids must be provided")

        # Create bind config
        bind_config = embedder_bind.EmbeddingConfig()
        bind_config.batch_size = config.batch_size
        bind_config.normalize = config.normalize
        bind_config.normalize_method = config.normalize_method

        # Convert single string to list if needed
        if isinstance(texts, str):
            texts = [texts]

        # Convert input_ids to 2D format if needed
        processed_input_ids = None
        if input_ids is not None:
            if len(input_ids) > 0 and isinstance(input_ids[0], int):
                # Single sequence: convert [1, 2, 3] to [[1, 2, 3]]
                processed_input_ids = [input_ids]
            else:
                # Multiple sequences: already in correct format [[1, 2], [3, 4]]
                processed_input_ids = input_ids

        # Pass both parameters, let the ABI handle validation
        embeddings = embedder_bind.ml_embedder_embed(self._handle, bind_config, texts, processed_input_ids)

        return embeddings

    def get_embedding_dim(self) -> int:
        """
        Get the embedding dimension of the model

        Returns:
            The embedding dimension in int
        """
        return embedder_bind.ml_embedder_embedding_dim(self._handle)
