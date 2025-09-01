"""
Backend implementations for Maximum Continual Training
"""

from .vllm_backend import LiteLLMModel
from .modal_backend import ModalBackend

__all__ = ["LiteLLMModel", "ModalBackend"]
