"""
Maximum Continual Training Client

Main client interface for the Maximum Continual Training library.
"""

import contextlib
from typing import List, Dict, Any, Optional
import os
import subprocess
import time
import sys
import modal
from pydantic import BaseModel
from smolagents import Tool
from .types import MessageT, PredictionResponseT, PredictionResponseWithRewardT
from .backend.vllm_backend import LiteLLMModel
from .backend.modal_backend import ModalBackend
from .agent import MaximumContinualAgent
from .backend.modal_functions import DEFAULT_BASE_MODEL

class MaximumContinualModel:
    """A model instance for Maximum Continual Training"""
    
    def __init__(
        self, 
        model_id: str,
        base_model: str,
        vllm_backend: LiteLLMModel,
        modal_backend: ModalBackend,
    ):
        self.model_id = model_id
        self.base_model = base_model
        self.vllm_backend = vllm_backend
        self.modal_backend = modal_backend
        self.agent = MaximumContinualAgent()
    
    def predict(
        self,
        messages: List[Dict[str, str]] | List[MessageT],
        tools: List[Tool] = [],
        additional_authorized_imports: List[str] = [],
        final_answer_model: Optional[BaseModel] = None,
        **kwargs
    ) -> PredictionResponseT:
        """Generate a prediction using the agentic workflow"""
        
        # Convert dict messages to MessageT if needed
        if messages and isinstance(messages[0], dict):
            messages = [MessageT(**msg) for msg in messages]
        
        # Use the agent to handle the agentic workflow
        return self.agent.run_agent_loop(
            messages=messages,
            tools=tools,
            final_answer_model=final_answer_model,
            vllm_backend=self.vllm_backend,
            model_id=self.model_id,
            additional_authorized_imports=additional_authorized_imports,
            **kwargs
        )
    
    def update(self, predictions: PredictionResponseWithRewardT) -> None:
        """Update the model with reward feedback"""
        self.modal_backend.update(self.model_id, predictions)


class MaximumContinual:
    """
    Main client for Maximum Continual Training
    
    Automatically handles Modal backend deployment and provides a clean interface
    for continual learning with LoRA models using reward-based feedback.
    
    Features:
    - Automatic Modal backend deployment  
    - Backend health monitoring
    - Model lifecycle management
    """
    
    def __init__(
        self, 
        modal_app_name: str = "maximum-continual",
        auto_deploy: bool = True
    ):
    # Setup and deploy Modal backend if requested
        self.modal_app_name = modal_app_name
        self.modal_backend = ModalBackend(app=modal_app_name, auto_deploy=auto_deploy)
        self.vllm_backend = self.modal_backend.get_model()
    
    @contextlib.contextmanager
    def init_model(
        self,
        model_id: str,
        **kwargs
    ) -> MaximumContinualModel:
        """Initialize a new model or fetch existing one"""
        
        # Try to fetch existing model first
        model_info = self.modal_backend.fetch_model(model_id)
        print("modal_model_info", model_info)
        if model_info is None:
            # Initialize new model
            init_result = self.modal_backend.initialize_model(
                base_model=DEFAULT_BASE_MODEL,
                model_id=model_id,
                **kwargs
            )
            
            if not init_result:
                raise RuntimeError(f"Failed to initialize model: {init_result.get('error')}")
        
        # Load the latest LoRA adapter if one exists
        lora_path = self.modal_backend.get_latest_lora_path(model_id)
        if lora_path:
            print(f"🔧 Loading LoRA adapter for model {model_id}: {lora_path}")
            load_result = self.modal_backend.load_lora_adapter(
                model_id
            )
            if load_result.success:
                print(f"✅ LoRA adapter loaded successfully")
            else:
                print(f"⚠️  Failed to load LoRA adapter: {load_result.message}")
        
        # Create and return model instance
        yield MaximumContinualModel(
            model_id=model_id,
            base_model=DEFAULT_BASE_MODEL,
            vllm_backend=self.vllm_backend,
            modal_backend=self.modal_backend,
        )
        
        if lora_path:
            self.modal_backend.unload_lora_adapter(model_id)