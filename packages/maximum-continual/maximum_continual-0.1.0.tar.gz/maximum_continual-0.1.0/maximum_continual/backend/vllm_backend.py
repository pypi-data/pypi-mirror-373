"""
vLLM Backend for Maximum Continual Training

Integrates with vLLM server using LiteLLM for LoRA-based predictions.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
import os
from maximum_continual.base_tools import Tool
import modal
from typing import List, Dict, Any, Optional
import litellm
from maximum_continual.backend.modal_backend import ModalBackend
from ..types import MessageT, PredictionResponseT, BaseMaximumContinualModel
from pydantic import BaseModel
import json
from .abstract import AbstractInferenceModel

def get_tool_json_schema(tool: Tool) -> dict:
    properties = deepcopy(tool.inputs)
    required = []
    for key, value in properties.items():
        if value["type"] == "any":
            value["type"] = "string"
        if not ("nullable" in value and value["nullable"]):
            required.append(key)
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }

   
class LiteLLMModel(AbstractInferenceModel):
    """Backend for vLLM inference with LoRA support"""
    
    def __init__(
        self, 
        modal_backend: ModalBackend,
        vllm_endpoint: str,
        base_model: str,
    ):
        self.vllm_endpoint = vllm_endpoint
        self.base_model = base_model
        self.modal_backend = modal_backend
        
        # Configure LiteLLM for vLLM
        litellm.set_verbose = True
        
    
    
    def predict(
        self, 
        messages: List[MessageT], 
        tools: Optional[List[Tool]] = None,
        model_id: Optional[str] = None,
        serial_only: bool = True,
        **kwargs
    ) -> MessageT:
        """Generate prediction using vLLM with LoRA adapter"""
        
        # Convert MessageT to dict format for LiteLLM
        message_dicts = []
        for msg in messages:
            message_dicts.append(msg.to_openai_message())
        
        # Determine which model/LoRA to use
        model_name = self.base_model
        # if model_id:
        #     lora_path = self.get_latest_lora_path(model_id)
        #     if lora_path:
        #         # Use the LoRA model name - vLLM filesystem resolver will find it
        #         # Convert path like "model_123/step_001_from_initial" to model name
        #         model_name = lora_path.replace("/", "_")
        
        # Prepare tools for LiteLLM function calling
        tool_schemas = []
        if tools:
            for tool in tools:
                tool_schemas.append(get_tool_json_schema(tool))
        
        # Make the completion request to vLLM via LiteLLM
        completion_kwargs = {
            "model": f"hosted_vllm/{model_name}",  # Use openai/ prefix for vLLM
            "messages": message_dicts,
            "api_base": self.vllm_endpoint,
        }
        if "max_tokens" in kwargs:
            completion_kwargs["max_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            completion_kwargs["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            completion_kwargs["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            completion_kwargs["top_k"] = kwargs["top_k"]
        if "frequency_penalty" in kwargs:
            completion_kwargs["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            completion_kwargs["presence_penalty"] = kwargs["presence_penalty"]
        if "stop" in kwargs:
            completion_kwargs["stop"] = kwargs["stop"]
        if tool_schemas:
            completion_kwargs["tools"] = tool_schemas
            completion_kwargs["tool_choice"] = "required"
            completion_kwargs['parallel_tool_calls'] = not serial_only
        
        response = litellm.completion(**completion_kwargs)
        
        # Process the response
        response_content = response.choices[0].message.content
        tool_calls = getattr(response.choices[0].message, 'tool_calls', None)
        if serial_only:
            tool_calls = [tool_calls[0]]

        # Create response message
        response_message = MessageT(
            role="assistant",
            content=response_content or "",
            tool_calls=[{
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in tool_calls] if tool_calls else None,
            metadata={
                "model_used": model_name,
                "model_id": model_id,
                "usage": response.usage.dict() if hasattr(response, 'usage') else None,
            }
        )
        print(json.dumps(response_message.model_dump(), indent=4))
        return response_message
        
