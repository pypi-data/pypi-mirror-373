"""
Maximum Continual Training API

A clean API for continual learning with LoRA models using reward-based feedback.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timezone
from abc import ABC, abstractmethod
import os
import subprocess
import time
import modal
from pydantic import BaseModel
import sys

# Type definitions
class MessageT(BaseModel):
    """A message in a conversation format"""
    role: str  # "system", "user", "assistant"
    content: str


class PredictionWithRewardT(BaseModel):
    """A prediction paired with its reward value"""
    prediction: str
    reward: float
    metadata: Optional[Dict[str, Any]] = None


class PredictionResponseT(BaseModel):
    """Response from model prediction"""
    prediction: str
    timestamp: str
    model_id: str
    full_response: str
    metadata: Dict[str, Any]


class ModelUpdateResponseT(BaseModel):
    """Response from model update with rewards"""
    success: bool
    new_model_path: str
    original_model_path: str
    training_metadata: Dict[str, Any]
    error: Optional[str] = None


# Abstract base classes
class AbstractContinualModel(ABC):
    """Abstract base class for continual learning models"""
    
    @abstractmethod
    def predict(
        self, 
        messages: List[MessageT],
        **kwargs
    ) -> PredictionResponseT:
        """Generate a prediction from the model"""
        pass
    
    @abstractmethod
    def update_with_reward(
        self, 
        predictions_with_rewards: List[PredictionWithRewardT],
        learning_rate: float = 2e-5
    ) -> ModelUpdateResponseT:
        """Update the model based on reward feedback"""
        pass


class AbstractContinualClient(ABC):
    """Abstract base class for continual learning clients"""
    
    @abstractmethod
    def init_model(
        self, 
        base_model: str, 
        model_id: str,
        **kwargs
    ) -> AbstractContinualModel:
        """Initialize a new continual learning model"""
        pass
    
    @abstractmethod
    def fetch_model(self, model_id: str) -> Optional[AbstractContinualModel]:
        """Fetch an existing model by ID"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List all available model IDs"""
        pass
    
    @abstractmethod
    def delete_model(self, model_id: str) -> bool:
        """Delete a model"""
        pass


class MaximumContinualModel(AbstractContinualModel):
    """A continually learning model that can be updated with reward feedback"""
    
    def __init__(
        self, 
        model_id: str, 
        base_model: str, 
        lora_path: str,
        modal_app_name: str = "maximum-continual"
    ):
        self.model_id = model_id
        self.base_model = base_model
        self.lora_path = lora_path
        self.modal_app_name = modal_app_name
        
    def predict(
        self, 
        messages: List[MessageT],
        **kwargs
    ) -> PredictionResponseT:
        """
        Generate a prediction from the model
        
        Args:
            messages: List of messages in conversation format
            **kwargs: Additional parameters for prediction
            
        Returns:
            PredictionResponseT with prediction and metadata
        """
        # Look up the prediction function
        try:
            predict_func = modal.Function.lookup(
                self.modal_app_name, "generate_prediction_modal"
            )
            
            # Convert messages to the format expected by the model
            current_time = datetime.now(timezone.utc).isoformat()
            
            # Call the Modal function
            result = predict_func.remote(
                messages=messages,
                model_id=self.model_id,
                base_model=self.base_model,
                lora_path=self.lora_path,
                current_time=current_time,
                **kwargs
            )
            
            return PredictionResponseT(
                prediction=result.get("prediction", ""),
                timestamp=result.get("timestamp", current_time),
                model_id=self.model_id,
                full_response=result.get("full_response", ""),
                metadata=result.get("metadata", {})
            )
            
        except Exception as e:
            # Fallback response for errors
            return PredictionResponseT(
                prediction="",
                timestamp=datetime.now(timezone.utc).isoformat(),
                model_id=self.model_id,
                full_response=f"Error: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def update_with_reward(
        self, 
        predictions_with_rewards: List[PredictionWithRewardT],
        learning_rate: float = 2e-5
    ) -> ModelUpdateResponseT:
        """
        Update the model based on reward feedback
        
        Args:
            predictions_with_rewards: List of predictions with their reward values
            learning_rate: Learning rate for the update
            
        Returns:
            ModelUpdateResponseT with update results
        """
        try:
            # Look up the training function
            update_func = modal.Function.lookup(
                self.modal_app_name, "update_model_modal"
            )
            
            # Process all predictions with rewards
            # For now, we'll combine all predictions and average the rewards
            # More sophisticated batching could be implemented here
            
            combined_text = "\n\n".join([p.prediction for p in predictions_with_rewards])
            avg_reward = sum(p.reward for p in predictions_with_rewards) / len(predictions_with_rewards)
            
            # Call the Modal function
            result = update_func.remote(
                lora_path=self.lora_path,
                completion_text=combined_text,
                reward_value=avg_reward,
                learning_rate=learning_rate,
                model_id=self.model_id
            )
            
            # Update our lora_path to the new one
            if result.get("success") and result.get("new_lora_path"):
                self.lora_path = result["new_lora_path"]
            
            return ModelUpdateResponseT(
                success=result.get("success", False),
                new_model_path=result.get("new_lora_path", ""),
                original_model_path=result.get("original_lora_path", ""),
                training_metadata=result.get("training_metadata", {}),
                error=result.get("error")
            )
            
        except Exception as e:
            return ModelUpdateResponseT(
                success=False,
                new_model_path="",
                original_model_path=self.lora_path,
                training_metadata={},
                error=str(e)
            )


class MaximumContinual(AbstractContinualClient):
    """
    Main client for Maximum Continual Training
    
    Automatically handles Modal backend deployment and provides a clean interface
    for continual learning with LoRA models using reward-based feedback.
    
    Features:
    - Abstract base class implementation
    - Automatic Modal backend deployment  
    - Backend health monitoring
    - Model lifecycle management
    """
    
    def __init__(self, modal_app_name: str = "maximum-continual", auto_deploy: bool = True):
        self.modal_app_name = modal_app_name
        self._models: Dict[str, MaximumContinualModel] = {}
        
        # Setup and deploy Modal backend if requested
        if auto_deploy:
            self._setup_modal_backend()
    
    def _setup_modal_backend(self) -> None:
        """Setup and deploy the Modal backend automatically"""
        print(f"🚀 Setting up Modal backend: {self.modal_app_name}")
        
        # Check Modal authentication
        if not self._check_modal_auth():
            print("❌ Modal authentication required. Run: modal setup")
            return
        
        # Deploy the backend
        if self._deploy_modal_backend():
            print("✅ Modal backend deployed successfully")
            
            # Wait for deployment to be ready
            if self._wait_for_deployment():
                print("✅ Modal backend is ready")
            else:
                print("⚠️  Modal backend may not be fully ready")
        else:
            print("⚠️  Modal backend deployment failed or was skipped")
    
    def _check_modal_auth(self) -> bool:
        """Check if Modal is properly authenticated"""
        try:
            # Try to list apps to check authentication
            result = subprocess.run(
                ["modal", "app", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _deploy_modal_backend(self) -> bool:
        """Deploy the Modal backend"""
        try:
            # Look for modal_backend.py in current directory
            backend_file = "modal_backend.py"
            if not os.path.exists(backend_file):
                print(f"❌ Backend file not found: {backend_file}")
                return False
            
            print(f"📦 Deploying {backend_file}...")
            process = subprocess.Popen(
                ["modal", "deploy", backend_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Handle potential None values for stdout/stderr
            stdout = process.stdout
            stderr = process.stderr
            
            while True:
                if stdout:
                    output = stdout.readline()
                    if output:
                        print(output.strip())
                        
                if stderr:
                    error = stderr.readline() 
                    if error:
                        print(error.strip(), file=sys.stderr)
                        
                if process.poll() is not None:
                    break
                    
            result_code = process.wait(timeout=1200)  # 5 minutes timeout
            
            if result_code == 0:
                print("✅ Modal deployment completed")
                return True
            else:
                print(f"❌ Modal deployment failed with exit code: {result_code}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Modal deployment timed out")
            return False
        except FileNotFoundError:
            print("❌ Modal CLI not found. Install with: pip install modal")
            return False
    
    def _wait_for_deployment(self, timeout: int = 60) -> bool:
        """Wait for the Modal deployment to be ready"""
        print("⏳ Waiting for deployment to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to lookup a function to test if deployment is ready
                test_func = modal.Function.lookup(
                    self.modal_app_name, "initialize_model_modal"
                )
                if test_func:
                    return True
            except Exception:
                pass
            
            time.sleep(2)
        
        return False
    
    def _validate_modal_backend(self) -> bool:
        """Validate that the Modal backend is working"""
        try:
            # Test all required functions exist
            required_functions = [
                "generate_prediction_modal",
                "update_model_modal", 
                "initialize_model_modal",
                "fetch_model_modal",
                "delete_model_modal"
            ]
            
            for func_name in required_functions:
                modal.Function.lookup(self.modal_app_name, func_name)
            
            return True
        except Exception as e:
            print(f"❌ Modal backend validation failed: {e}")
            return False
    
    def get_backend_status(self) -> Dict[str, Any]:
        """Get the status of the Modal backend"""
        return {
            "app_name": self.modal_app_name,
            "authenticated": self._check_modal_auth(),
            "backend_valid": self._validate_modal_backend(),
            "functions_available": self._list_available_functions()
        }
    
    def _list_available_functions(self) -> List[str]:
        """List available Modal functions"""
        try:
            # This is a simplified check - in practice you'd use Modal's API
            required_functions = [
                "generate_prediction_modal",
                "update_model_modal", 
                "initialize_model_modal",
                "fetch_model_modal",
                "delete_model_modal"
            ]
            
            available = []
            for func_name in required_functions:
                try:
                    modal.Function.lookup(self.modal_app_name, func_name)
                    available.append(func_name)
                except Exception:
                    pass
            
            return available
        except Exception:
            return []
    
    def deploy_backend(self) -> bool:
        """Manually deploy the Modal backend"""
        return self._deploy_modal_backend()
    
    def setup_backend(self) -> None:
        """Manually setup the complete Modal backend (auth + deploy + validate)"""
        self._setup_modal_backend()
    
    def init_model(
        self, 
        base_model: str, 
        model_id: str,
        **kwargs
    ) -> MaximumContinualModel:
        """
        Initialize a new continual learning model
        
        Args:
            base_model: Base model name (e.g., "Qwen/Qwen3-14B")
            model_id: Unique identifier for this model instance
            **kwargs: Additional model configuration
            
        Returns:
            MaximumContinualModel instance
        """
        # Create initial LoRA path for the model
        # This would call a Modal function to set up the initial LoRA
        try:
            init_func = modal.Function.lookup(
                self.modal_app_name, "initialize_model_modal"
            )
            
            result = init_func.remote(
                base_model=base_model,
                model_id=model_id,
                **kwargs
            )
            
            lora_path = result.get("lora_path", f"model_{model_id}/initial")
            
        except Exception as e:
            print(f"Warning: Could not initialize via Modal: {e}")
            # Fallback to local path generation
            lora_path = f"model_{model_id}/initial"
        
        model = MaximumContinualModel(
            model_id=model_id,
            base_model=base_model,
            lora_path=lora_path,
            modal_app_name=self.modal_app_name
        )
        
        self._models[model_id] = model
        return model
    
    def fetch_model(self, model_id: str) -> Optional[MaximumContinualModel]:
        """
        Fetch an existing model by ID
        
        Args:
            model_id: The model ID to fetch
            
        Returns:
            MaximumContinualModel instance if found, None otherwise
        """
        if model_id in self._models:
            return self._models[model_id]
        
        # Try to fetch from Modal/storage
        try:
            fetch_func = modal.Function.lookup(
                self.modal_app_name, "fetch_model_modal"
            )
            
            result = fetch_func.remote(model_id=model_id)
            
            if result.get("success"):
                model = MaximumContinualModel(
                    model_id=model_id,
                    base_model=result.get("base_model", ""),
                    lora_path=result.get("lora_path", ""),
                    modal_app_name=self.modal_app_name
                )
                self._models[model_id] = model
                return model
                
        except Exception as e:
            print(f"Could not fetch model {model_id}: {e}")
        
        return None
    
    def list_models(self) -> List[str]:
        """List all available model IDs"""
        return list(self._models.keys())
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a model"""
        if model_id in self._models:
            del self._models[model_id]
            
            # Also try to delete from Modal storage
            try:
                delete_func = modal.Function.lookup(
                    self.modal_app_name, "delete_model_modal"
                )
                delete_func.remote(model_id=model_id)
            except Exception as e:
                print(f"Warning: Could not delete from remote storage: {e}")
            
            return True
        return False


# Convenience functions for quick usage
def create_client(
    modal_app_name: str = "maximum-continual", 
    auto_deploy: bool = True
) -> MaximumContinual:
    """Create a MaximumContinual client with optional auto-deployment"""
    return MaximumContinual(modal_app_name=modal_app_name, auto_deploy=auto_deploy)


def quick_predict(
    model_id: str, 
    messages: List[MessageT], 
    base_model: str = "Qwen/Qwen3-14B"
) -> PredictionResponseT:
    """Quick prediction without managing client state"""
    client = create_client()
    model = client.fetch_model(model_id) or client.init_model(base_model, model_id)
    return model.predict(messages)