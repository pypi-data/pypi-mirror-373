"""
Type definitions for Maximum Continual Training
"""

import json
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, field_validator
from abc import ABC, abstractmethod


class ToolCallFunctionT(BaseModel):
    """Function call within a tool call"""
    name: str
    arguments: Dict[str, Any]
    
    @field_validator('arguments', mode='before')
    @classmethod
    def validate_arguments(cls, v):
        """Convert string arguments to dict if needed"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string for arguments: {e}")
        return v

    


class ToolCallT(BaseModel):
    """Tool call structure"""
    id: Optional[str] = None
    type: str = "function"
    function: ToolCallFunctionT


class MessageT(BaseModel):
    """Message format for chat interactions"""
    role: str
    content: str
    tool_calls: Optional[List[ToolCallT]] = None
    tool_call_id: Optional[str] = None
    metadata : Optional[Dict[str, Any]] = None

    def to_openai_message(self) -> Dict[str, Any]:
        """Convert to OpenAI message format"""
        message = {}
        message["role"] = self.role
        if self.content:
            message["content"] = self.content
        if self.tool_calls:
            message["tool_calls"] = [{
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": json.dumps(tool_call.function.arguments)
                }
            } for tool_call in self.tool_calls]
        if self.tool_call_id:
            message["tool_call_id"] = self.tool_call_id
        return message

    def to_transformers_message(self) -> Dict[str, Any]:
        message = {}
        message["role"] = self.role
        if self.content:
            message["content"] = self.content
        if self.tool_calls:
            message["tool_calls"] = [{
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            } for tool_call in self.tool_calls]
        if self.tool_call_id:
            message["tool_call_id"] = self.tool_call_id
        return message

class PredictionResponseT(BaseModel):
    """Response from a prediction call"""
    final_response: BaseModel
    messages: List[MessageT]
    metadata: Optional[Dict[str, Any]] = None



class PredictionResponseWithRewardT(BaseModel):
    """Prediction response with associated reward"""
    prediction: PredictionResponseT
    reward: float


class BaseMaximumContinualModel(ABC):
    """Abstract base class for Maximum Continual models"""
    
    @abstractmethod
    def predict(
        self, 
        messages: List[MessageT], 
        tools: Optional[List[Any]] = None,
        final_answer_model: Optional[BaseModel] = None,
        **kwargs
    ) -> PredictionResponseT:
        """Generate a prediction using the model"""
        pass
    
    @abstractmethod
    def update(
        self, 
        predictions: PredictionResponseWithRewardT
    ) -> Dict[str, Any]:
        """Update the model with reward feedback"""
        pass

    @abstractmethod
    def get_latest_lora_path(
        self,
        model_id: str
    ) -> str:
        """Get the latest lora path for a model"""
        pass
