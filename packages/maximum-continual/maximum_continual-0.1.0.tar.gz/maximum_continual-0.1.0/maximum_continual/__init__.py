"""
Maximum Continual Training Library

A clean API for continual learning with LoRA models using reward-based feedback.
"""

from .client import MaximumContinual
from .base_tools import Tool
from .types import (
    MessageT,
    PredictionResponseT,
    PredictionResponseWithRewardT,
)
from .system_prompt import fetch_default_system_prompt

__version__ = "0.1.0"

__all__ = [
    "MaximumContinual",
    "MessageT", 
    "PredictionResponseT",
    "PredictionResponseWithRewardT",
    "fetch_default_system_prompt",
    "Tool"
]
