from abc import ABC, abstractmethod
from nexaai.common import ProfilingData
from nexaai.utils.model_manager import auto_download_model

class BaseModel(ABC):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.eject()

    def __del__(self):
        self.eject()

    @classmethod
    @auto_download_model
    def from_(cls, name_or_path: str, **kwargs) -> "BaseModel":
        """
        initialize model from (1) HF (2) if not found, then from local path
        """

        return cls._load_from(name_or_path, **kwargs)

    @classmethod
    @abstractmethod
    def _load_from(cls, name_or_path: str, **kwargs) -> "BaseModel":
        """
        Model-specific loading logic. Must be implemented by each model type.
        Called after model is available locally.
        """  
        pass

    @abstractmethod
    def eject(self):
        pass

    def get_profiling_data(self) -> ProfilingData:
        pass
