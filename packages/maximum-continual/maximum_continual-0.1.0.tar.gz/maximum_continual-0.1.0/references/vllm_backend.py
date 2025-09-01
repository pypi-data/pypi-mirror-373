import json
from typing import Any

import aiohttp
import modal
N_GPU = 4
GPU_TYPE = "H100"
GPUS_USED =f"{GPU_TYPE}:{N_GPU}"
MODEL_NAME = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
def install_vllm_dependencies():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    model_name = MODEL_NAME
    _ = AutoTokenizer.from_pretrained(model_name)
    _ = AutoModelForCausalLM.from_pretrained(model_name)
hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)
lora_vol = modal.Volume.from_name("continual-lora-models", create_if_missing=True)
vllm_image = (
   modal.Image.debian_slim(python_version="3.12")
   .apt_install("wget")
   .uv_pip_install("vllm==0.10.1", gpu=f"{GPU_TYPE}:1")
   .uv_pip_install("huggingface_hub[hf_transfer]", "accelerate")
#    .run_function(install_vllm_dependencies, volumes={
#         "/root/.cache/huggingface": hf_cache_vol,
#         "/root/.cache/vllm": vllm_cache_vol,
#     }, gpu=f"{GPU_TYPE}:1")
   .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})  # faster model transfers
)


vllm_image = vllm_image.env({"VLLM_USE_V1": "1"})
app = modal.App("example-vllm-inference")

MINUTES = 60  # seconds
VLLM_PORT = 8000
FAST_BOOT=True

@app.function(
    image=vllm_image,
    gpu=GPUS_USED,
    scaledown_window=15 * MINUTES,  # how long should we stay up with no requests?
    timeout=10 * MINUTES,  # how long should we wait for container start?
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
        "/lora_models": lora_vol,  # Mount LoRA models volume
    },
)
@modal.concurrent(  # how many requests can one replica handle? tune carefully!
    max_inputs=32
)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * MINUTES)
def serve():
    import subprocess

    cmd = [
        "vllm",
        "serve",
        "--uvicorn-log-level=info",
        MODEL_NAME,
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        # Enable LoRA support
        "--enable-lora",
        "--max-lora-rank", "64",  # Configurable max rank for LoRA adapters
        "--max-loras", "8",  # Max number of LoRA adapters to keep in memory
    ]

    # Set environment variables for dynamic LoRA loading via filesystem resolver
    import os
    os.environ["VLLM_ALLOW_RUNTIME_LORA_UPDATING"] = "True"
    os.environ["VLLM_PLUGINS"] = "lora_filesystem_resolver"
    os.environ["VLLM_LORA_RESOLVER_CACHE_DIR"] = "/lora_models"

    # enforce-eager disables both Torch compilation and CUDA graph capture
    # default is no-enforce-eager. see the --compilation-config flag for tighter control
    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]

    # assume multiple GPUs are for splitting up large matrix multiplications
    cmd += ["--tensor-parallel-size", str(N_GPU)]

    print(cmd)

    subprocess.Popen(" ".join(cmd), shell=True)


