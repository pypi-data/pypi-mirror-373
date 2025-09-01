"""
Tests for agentic workflow
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel

from maximum_continual.agent import MaximumContinualAgent
from maximum_continual.types import MessageT, PredictionResponseT
from maximum_continual.tools import CodeExecutorTool, FinalAnswerTool


class TestFinalModel(BaseModel):
    content: str
    score: float = 1.0


def test_agent_initialization():
    """Test agent initialization"""
    agent = MaximumContinualAgent()
    assert agent.python_executor is not None


def test_code_executor_tool():
    """Test CodeExecutorTool"""
    with patch('smolagents.LocalPythonExecutor') as mock_executor:
        mock_executor.return_value.execute.return_value = "42"
        
        tool = CodeExecutorTool(mock_executor.return_value, [])
        result = tool.execute("print(2 + 2)")
        
        assert "42" in result or result == "42"


def test_final_answer_tool():
    """Test FinalAnswerTool"""
    final_model = TestFinalModel
    tool = FinalAnswerTool(final_model)
    
    answer = {"content": "Final answer", "score": 0.9}
    result = tool.execute(answer)
    
    assert isinstance(result, TestFinalModel)
    assert result.content == "Final answer"
    assert result.score == 0.9


def test_final_answer_tool_no_model():
    """Test FinalAnswerTool without model"""
    tool = FinalAnswerTool(None)
    answer = {"content": "Final answer"}
    result = tool.execute(answer)
    
    assert result == answer


def test_agent_loop_final_answer():
    """Test agent loop reaching final answer"""
    agent = MaximumContinualAgent()
    
    # Mock vLLM backend
    mock_backend = Mock()
    mock_backend._get_latest_lora_path.return_value = "test/path"
    
    # Mock prediction with final_answer tool call
    mock_prediction = PredictionResponseT(
        final_response={"content": "test"},
        messages=[
            MessageT(
                role="assistant",
                content="I'll provide the final answer",
                tool_calls=[{
                    "id": "1",
                    "function": {
                        "name": "final_answer",
                        "arguments": '{"answer": {"content": "Final result"}}'
                    }
                }]
            )
        ]
    )
    
    mock_backend.predict.return_value = mock_prediction
    
    messages = [MessageT(role="user", content="Test question")]
    
    with patch.object(agent.python_executor, 'execute'):
        result = agent.run_agent_loop(
            messages=messages,
            tools=[],
            final_answer_model=TestFinalModel,
            vllm_backend=mock_backend,
            model_id="test-model"
        )
    
    assert isinstance(result, PredictionResponseT)
    assert result.metadata["model_id"] == "test-model"


def test_agent_loop_max_iterations():
    """Test agent loop hitting max iterations"""
    agent = MaximumContinualAgent()
    
    # Mock vLLM backend that never calls final_answer
    mock_backend = Mock()
    mock_backend._get_latest_lora_path.return_value = "test/path"
    
    mock_prediction = PredictionResponseT(
        final_response={"content": "thinking"},
        messages=[MessageT(role="assistant", content="Let me think...")]
    )
    
    mock_backend.predict.return_value = mock_prediction
    
    messages = [MessageT(role="user", content="Test question")]
    
    result = agent.run_agent_loop(
        messages=messages,
        tools=[],
        final_answer_model=None,
        vllm_backend=mock_backend,
        model_id="test-model",
        max_iterations=2
    )
    
    assert isinstance(result, PredictionResponseT)
    assert result.metadata.get("max_iterations_reached") is True
    assert result.metadata["iterations"] == 2
