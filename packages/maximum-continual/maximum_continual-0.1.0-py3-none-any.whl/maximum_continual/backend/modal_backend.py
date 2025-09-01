"""
Modal Backend for Maximum Continual Training

Handles model initialization, fetching, and updates using Modal functions.
"""

from typing import Dict, Any, Optional, List
from maximum_continual.backend.modal_functions import DEFAULT_BASE_MODEL, LoraInfoT
import modal
import requests
from maximum_continual.types import PredictionResponseWithRewardT
from maximum_continual.backend.abstract import AbstractInferenceModel
from pydantic import BaseModel
import os
import subprocess
import sys
import time
class LoadResponseT(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None

class ModalBackend:
    """Backend for Modal-based model operations"""
    def __init__(self, app: str, auto_deploy: bool = True):
        self.app = app
        if auto_deploy:
            self._setup_modal_backend()
    
    def _setup_modal_backend(self) -> None:
        """Setup and deploy the Modal backend automatically"""
        print(f"🚀 Setting up Modal backend: {self.app}")
        
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
            # Look for modal_backend.py in current directory or backend directory
            backend_files = [
                "modal_functions.py",
                os.path.join(os.path.dirname(__file__), "modal_functions.py")
            ]
            
            backend_file = None
            for file in backend_files:
                if os.path.exists(file):
                    backend_file = file
                    break
            
            if not backend_file:
                print(f"❌ Backend file not found. Tried: {backend_files}")
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
                    self.app, "initialize_model_modal"
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
                modal.Function.lookup(self.app, func_name)
            
            return True
        except Exception as e:
            print(f"❌ Modal backend validation failed: {e}")
            return False
    
    def get_backend_status(self) -> Dict[str, Any]:
        """Get the status of the Modal backend"""
        return {
            "app_name": self.app,
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
                    modal.Function.lookup(self.app, func_name)
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

    def initialize_model(
        self, 
        base_model: str, 
        model_id: str,
        **kwargs
    ) -> LoraInfoT | None:
        """Initialize a new model"""
        # Get the Modal function
        initialize_func = modal.Function.from_name(self.app, "initialize_model_modal")
        result = initialize_func.remote(base_model, model_id, **kwargs)
        if result is None:
            return None
        return LoraInfoT(**result)
    
    def fetch_model(self, model_id: str) -> LoraInfoT | None:
        """Fetch model information"""
        fetch_func = modal.Function.from_name(self.app, "fetch_model_modal")
        result = fetch_func.remote(model_id)
        if result is None:
            return None
        return LoraInfoT(**result)
    
    def update(
        self, 
        model_id: str,
        predictions: List[PredictionResponseWithRewardT]
    ):
        """Update model with reward feedback using messages and chat template"""
        # Extract information from the prediction response
            # Call the Modal update function with messages
        update_func = modal.Function.from_name(self.app, "update_model_modal_batch")
        _ = update_func.remote(
            batch_messages=[
                ([
                   msg.to_transformers_message() for msg in prediction.prediction.messages
                ], prediction.reward)
                for prediction in predictions
            ], 
            model_id=model_id,
            learning_rate=2e-5,
        )
        
    
    def delete_model(self, model_id: str) -> None:
        """Delete a model"""
        delete_func = modal.Function.from_name(self.app, "delete_model_modal")
        _ = delete_func.remote(model_id)
        return None
    
    def get_vllm_endpoint(self) -> str:
        """Get the VLLM endpoint"""
        return modal.Function.from_name(self.app, "serve").get_web_url() + "/v1"

    def get_model(self)-> AbstractInferenceModel:
        """Get the VLLM backend"""
        from .vllm_backend import LiteLLMModel
        return LiteLLMModel(vllm_endpoint=self.get_vllm_endpoint(), modal_backend=self, base_model=DEFAULT_BASE_MODEL)

    def get_latest_lora_path(self, model_id: str) -> Optional[str]:
        """Get the latest LoRA path for a model_id from Modal backend"""
        model_info = self.fetch_model(model_id)
        if model_info is None:
            return None
        return model_info.full_lora_path
    
    def load_lora_adapter(self, model_id: str) -> LoadResponseT:
        """Load a LoRA adapter by making HTTP request to vLLM endpoint"""
        lora_info = self.fetch_model(model_id)
        if lora_info is None:
            return LoadResponseT(success=False, message=f"Model {model_id} not found")
        lora_name = lora_info.lora_name
        lora_path = lora_info.full_lora_path
        vllm_endpoint = self.get_vllm_endpoint()
        url = f"{vllm_endpoint}/load_lora_adapter"
        print(f"Loading LoRA adapter for model {model_id} from {lora_path}")
        payload = {
            "lora_name": lora_name,
            "lora_path": lora_path,
        }
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                return LoadResponseT(success=True, message=f"LoRA adapter '{lora_name}' loaded successfully")
            else:
                return LoadResponseT(success=False, message=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return LoadResponseT(success=False, message=f"Request failed: {str(e)}")
    
    def unload_lora_adapter(self, model_id: str) -> LoadResponseT:
        """Unload a LoRA adapter by making HTTP request to vLLM endpoint"""
        vllm_endpoint = self.get_vllm_endpoint()
        url = f"{vllm_endpoint}/unload_lora_adapter"
        lora_info = self.fetch_model(model_id)
        lora_name = lora_info.lora_name
        print(f"Unloading LoRA adapter for model {lora_name}")
        payload = {
            "lora_name": lora_name,
            "model_id": model_id
        }
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(response.text)
            return LoadResponseT(success=True, message=f"LoRA adapter '{lora_name}' unloaded successfully")
        else:
            print(f"HTTP {response.status_code}: {response.text}")
            return LoadResponseT(success=False, error=f"HTTP {response.status_code}: {response.text}")
            
