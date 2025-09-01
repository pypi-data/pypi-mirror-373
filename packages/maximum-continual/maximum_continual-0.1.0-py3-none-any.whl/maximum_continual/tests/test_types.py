"""
Tests for type definitions
"""

import pytest
from pydantic import ValidationError

from maximum_continual.types import MessageT, PredictionResponseT, PredictionResponseWithRewardT


def test_message_creation():
    """Test MessageT creation"""
    message = MessageT(role="user", content="Hello")
    assert message.role == "user"
    assert message.content == "Hello"
    assert message.tool_calls is None


def test_message_with_tool_calls():
    """Test MessageT with tool calls"""
    tool_calls = [{"id": "1", "function": {"name": "test"}}]
    message = MessageT(
        role="assistant", 
        content="", 
        tool_calls=tool_calls,
        tool_call_id="1"
    )
    assert message.tool_calls == tool_calls
    assert message.tool_call_id == "1"


def test_prediction_response():
    """Test PredictionResponseT"""
    final_response = {"content": "Answer"}
    messages = [MessageT(role="user", content="Question")]
    
    response = PredictionResponseT(
        final_response=final_response,
        messages=messages,
        metadata={"model": "test"}
    )
    
    assert response.final_response == final_response
    assert len(response.messages) == 1
    assert response.metadata["model"] == "test"


def test_prediction_with_reward():
    """Test PredictionResponseWithRewardT"""
    prediction = PredictionResponseT(
        final_response={"content": "Answer"},
        messages=[MessageT(role="user", content="Question")]
    )
    
    prediction_with_reward = PredictionResponseWithRewardT(
        prediction=prediction,
        reward=0.8
    )
    
    assert prediction_with_reward.reward == 0.8
    assert prediction_with_reward.prediction == prediction


def test_invalid_reward_range():
    """Test that rewards outside valid range are handled"""
    prediction = PredictionResponseT(
        final_response={"content": "Answer"},
        messages=[MessageT(role="user", content="Question")]
    )
    
    # Should accept any float value (validation can be added later if needed)
    prediction_with_reward = PredictionResponseWithRewardT(
        prediction=prediction,
        reward=-1.0  # Negative reward should be allowed
    )
    
    assert prediction_with_reward.reward == -1.0
