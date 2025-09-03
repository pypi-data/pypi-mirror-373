from typing import List, Optional, Sequence, Union
from abc import abstractmethod
from dataclasses import dataclass

from nexaai.base import BaseModel
from nexaai.common import PluginID


@dataclass
class RerankConfig:
    """Configuration for reranking."""
    batch_size: int = 1
    normalize: bool = True
    normalize_method: str = "softmax"  # "softmax" | "min-max" | "none"


class Reranker(BaseModel):
    """Abstract base class for reranker models."""

    def __init__(self):
        """Initialize base Reranker class."""
        pass

    @classmethod
    def _load_from(cls,
                   model_path: str,
                   tokenizer_file: str = "tokenizer.json",
                   plugin_id: Union[PluginID, str] = PluginID.LLAMA_CPP,
                   device_id: Optional[str] = None
        ) -> 'Reranker':
        """Load reranker model from local path, routing to appropriate implementation."""
        # Check plugin_id value for routing - handle both enum and string
        plugin_value = plugin_id.value if isinstance(plugin_id, PluginID) else plugin_id
        
        if plugin_value == "mlx":
            from nexaai.rerank_impl.mlx_rerank_impl import MLXRerankImpl
            return MLXRerankImpl._load_from(model_path, tokenizer_file, plugin_id, device_id)
        else:
            from nexaai.rerank_impl.pybind_rerank_impl import PyBindRerankImpl
            return PyBindRerankImpl._load_from(model_path, tokenizer_file, plugin_id, device_id)

    @abstractmethod
    def load_model(self, model_path: str, extra_data: Optional[str] = None) -> bool:
        """Load model from path."""
        pass

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        config: Optional[RerankConfig] = None,
    ) -> List[float]:
        """Rerank documents given a query."""
        pass
