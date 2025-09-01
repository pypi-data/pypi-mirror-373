from abc import ABC, abstractmethod
from typing import List, Optional
from maximum_continual.base_tools import Tool
from maximum_continual.types import MessageT

class AbstractInferenceModel(ABC):
    """Abstract model class"""
    @abstractmethod
    def predict(self, messages: List[MessageT], tools: Optional[List[Tool]] = None, model_id: Optional[str] = None, **kwargs) -> MessageT:
        """Generate prediction using vLLM with LoRA adapter"""
        raise NotImplementedError("Subclasses must implement this method")
