"""
Tests for MaximumContinual client
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel

from maximum_continual import MaximumContinual, MessageT, PredictionResponseWithRewardT
from maximum_continual.types import PredictionResponseT


class TestFinalAnswerModel(BaseModel):
    """Test model for final answers"""
    content: str
    confidence: float = 0.8


@pytest.fixture
def mock_vllm_backend():
    """Mock vLLM backend"""
    with patch('maximum_continual.backend.vllm_backend.VLLMBackend') as mock:
        yield mock


@pytest.fixture
def mock_modal_backend():
    """Mock Modal backend"""
    with patch('maximum_continual.backend.modal_backend.ModalBackend') as mock:
        yield mock


def test_client_initialization():
    """Test MaximumContinual client initialization"""
    with patch('maximum_continual.backend.vllm_backend.VLLMBackend'):
        with patch('maximum_continual.backend.modal_backend.ModalBackend'):
            client = MaximumContinual()
            assert client is not None


def test_init_model_new(mock_modal_backend):
    """Test initializing a new model"""
    # Mock the backend responses
    mock_modal_backend.return_value.fetch_model.return_value = {"success": False}
    mock_modal_backend.return_value.initialize_model.return_value = {"success": True}
    
    with patch('maximum_continual.backend.vllm_backend.VLLMBackend'):
        client = MaximumContinual()
        model = client.init_model(
            base_model="Qwen/Qwen3-14B",
            model_id="test-model"
        )
        
        assert model.model_id == "test-model"
        assert model.base_model == "Qwen/Qwen3-14B"


def test_init_model_existing(mock_modal_backend):
    """Test fetching an existing model"""
    # Mock the backend to return existing model
    mock_modal_backend.return_value.fetch_model.return_value = {"success": True}
    
    with patch('maximum_continual.backend.vllm_backend.VLLMBackend'):
        client = MaximumContinual()
        model = client.init_model(
            base_model="Qwen/Qwen3-14B",
            model_id="existing-model"
        )
        
        assert model.model_id == "existing-model"


def test_model_predict():
    """Test model prediction"""
    # Mock the agent and backends
    with patch('maximum_continual.backend.vllm_backend.VLLMBackend'):
        with patch('maximum_continual.backend.modal_backend.ModalBackend') as mock_modal:
            mock_modal.return_value.fetch_model.return_value = {"success": True}
            
            client = MaximumContinual()
            model = client.init_model(
                base_model="Qwen/Qwen3-14B",
                model_id="test-model"
            )
            
            # Mock the agent's run_agent_loop method
            mock_response = PredictionResponseT(
                final_response={"content": "Test response"},
                messages=[MessageT(role="assistant", content="Test response")],
                metadata={"model_id": "test-model"}
            )
            
            with patch.object(model.agent, 'run_agent_loop', return_value=mock_response):
                messages = [{"role": "user", "content": "Test message"}]
                response = model.predict(messages)
                
                assert isinstance(response, PredictionResponseT)
                assert response.final_response == {"content": "Test response"}


def test_model_update():
    """Test model update"""
    with patch('maximum_continual.backend.vllm_backend.VLLMBackend'):
        with patch('maximum_continual.backend.modal_backend.ModalBackend') as mock_modal:
            mock_modal.return_value.fetch_model.return_value = {"success": True}
            mock_modal.return_value.update.return_value = {"success": True}
            
            client = MaximumContinual()
            model = client.init_model(
                base_model="Qwen/Qwen3-14B",
                model_id="test-model"
            )
            
            # Create prediction with reward
            prediction = PredictionResponseT(
                final_response={"content": "Test response"},
                messages=[MessageT(role="assistant", content="Test response")],
                metadata={"model_id": "test-model"}
            )
            
            prediction_with_reward = PredictionResponseWithRewardT(
                prediction=prediction,
                reward=0.8
            )
            
            result = model.update(prediction_with_reward)
            assert result["success"] is True
