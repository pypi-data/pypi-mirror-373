"""
Modal Backend for Maximum Continual Training

This module provides the Modal functions that support the MaximumContinual API.
It abstracts the original stock-specific code to work with generic message formats.
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import modal

# Default base model
DEFAULT_BASE_MODEL = "Qwen/Qwen3-14B"

# Modal app for generic continual learning
app = modal.App("maximum-continual")

# Modal volume for storing LoRA models
lora_vol = modal.Volume.from_name("continual-lora-models", create_if_missing=True)


def install_dependencies():
    """Install the base model dependencies"""
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
    _ = AutoModelForCausalLM.from_pretrained(DEFAULT_BASE_MODEL, trust_remote_code=True)
    _ = AutoTokenizer.from_pretrained(DEFAULT_BASE_MODEL, trust_remote_code=True)


# Modal image with dependencies
base_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("transformers>=4.35.0", "torch>=2.6.0")
    .run_function(install_dependencies)
    .pip_install(
        "peft>=0.7.0",
        "bitsandbytes>=0.41.0", 
        "accelerate>=0.24.0",
        "datasets>=2.14.0",
        "tqdm>=4.65.0",
        "requests>=2.31.0",
        "pandas>=2.1.0",
    )
    .apt_install("git", "wget")
)


@app.function(
    image=base_image,
    gpu="A100",
    timeout=3600,
    volumes={"/lora_models": lora_vol},
    max_containers=2,
)
def generate_prediction_modal(
    messages: List[Dict[str, str]],
    model_id: str,
    base_model: str,
    lora_path: str,
    current_time: str,
    max_new_tokens: int = 2048,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> Dict[str, Any]:
    """Generate a prediction using the LoRA model"""
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  # type: ignore
    from peft import PeftModel  # type: ignore

    # Load base model
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
    )

    base_model_instance = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map="auto", 
        quantization_config=bnb_config,
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)

    # Load LoRA adapter if it exists
    full_lora_path = f"/lora_models/{lora_path}"
    if os.path.exists(full_lora_path):
        model = PeftModel.from_pretrained(base_model_instance, full_lora_path)
        print(f"Loaded LoRA from {full_lora_path}")
    else:
        model = base_model_instance
        print(f"LoRA path {full_lora_path} not found, using base model")

    # Set padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # Convert messages to the format expected by tokenizer
    # Assuming messages is a list of dicts with 'role' and 'content' keys
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Generate prediction
    prompt = tokenizer.apply_chat_template(
        formatted_messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(
        model.device
    )

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_text = tokenizer.decode(
        output_ids[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
    )
    
    print(f"Generated text: {generated_text}")

    return {
        "success": True,
        "timestamp": current_time,
        "model_id": model_id,
        "prediction": generated_text,
        "full_response": generated_text,
        "lora_path": lora_path,
        "base_model": base_model,
        "metadata": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "prompt_length": len(prompt),
            "response_length": len(generated_text),
        },
        "error": None,
    }


@app.function(
    image=base_image,
    gpu="A100", 
    timeout=3600,
    volumes={"/lora_models": lora_vol},
    max_containers=2,
)
def update_model_modal(
    lora_path: str,
    completion_text: str,
    reward_value: float,
    model_id: str,
    learning_rate: float = 2e-5,
) -> Dict[str, Any]:
    """Update a LoRA model with reward feedback"""
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  # type: ignore
    from peft import PeftModel, LoraConfig, get_peft_model, TaskType  # type: ignore

    # Extract base model from the model_id or use default
    # You might want to store this metadata somewhere
    base_model = DEFAULT_BASE_MODEL  # Could be made configurable

    # Load base model
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
    )

    base_model_instance = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map="auto",
        quantization_config=bnb_config,
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)

    # Set padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # Parse LoRA path to extract model info and training lineage
    path_parts = lora_path.split("/")
    if len(path_parts) >= 2:
        model_folder = path_parts[0]  # e.g., "model_123"
        step_folder = path_parts[1]   # e.g., "step_001_from_initial" or "initial"
    else:
        model_folder = f"model_{model_id}"
        step_folder = "initial"

    full_lora_path = f"/lora_models/{model_folder}/{step_folder}"

    if os.path.exists(full_lora_path):
        # Load existing LoRA
        model = PeftModel.from_pretrained(base_model_instance, full_lora_path)
        print(f"Loaded LoRA from evolutionary chain: {full_lora_path}")

        # Ensure LoRA modules are trainable
        for name, param in model.named_parameters():
            if any(lora_key in name for lora_key in ["lora_A", "lora_B", "lora_embedding"]):
                param.requires_grad = True
    else:
        # Create new LoRA
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        model = get_peft_model(base_model_instance, lora_config)
        print(f"Created new LoRA model for: {model_folder}")

    print("Enabling gradient checkpointing...")
    model.gradient_checkpointing_enable()

    # Prepare model for training
    model.train()

    # Create optimizer for trainable parameters
    trainable_params = [p for n, p in model.named_parameters() if p.requires_grad]
    print(f"Found {len(trainable_params)} trainable parameters")

    if not trainable_params:
        raise ValueError("No trainable parameters found in the model")

    optimizer = torch.optim.AdamW(trainable_params, lr=learning_rate)

    # Tokenize the completion text for training
    inputs = tokenizer(
        completion_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    ).to(model.device)

    label_ids = inputs["input_ids"]
    output_length = label_ids.shape[1] - 1

    print(f"Training on completion with {output_length} tokens, reward: {reward_value:.3f}")

    # Token-by-token training with reward weighting
    total_loss = 0.0
    tokens_per_update = 32

    reward_tensor = torch.ones(output_length, device=model.device, requires_grad=True) * reward_value

    for i in range(0, output_length, tokens_per_update):
        optimizer.zero_grad()
        chunk_end = min(i + tokens_per_update, output_length)
        chunk_size = chunk_end - i
        chunk_loss = None

        for j in range(i, chunk_end):
            current_length = j + 1
            current_input_ids = label_ids[:, :current_length]

            if current_length < label_ids.shape[1]:
                target_id = label_ids[:, current_length]

                outputs = model(
                    input_ids=current_input_ids,
                    attention_mask=torch.ones_like(current_input_ids),
                )
                logits = outputs.logits[:, -1, :]

                log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
                token_log_prob = log_probs[0, target_id[0]]
                token_loss = -token_log_prob * reward_tensor[j]

                if chunk_loss is None:
                    chunk_loss = token_loss
                else:
                    chunk_loss = chunk_loss + token_loss

                total_loss += token_loss.detach()

        if chunk_size > 0 and chunk_loss is not None:
            chunk_loss = chunk_loss / chunk_size
            chunk_loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=1.0)
            optimizer.step()

        if i % (tokens_per_update * 4) == 0:
            torch.cuda.empty_cache()

    avg_loss = total_loss / max(output_length, 1)
    print(f"Reward: {reward_value:.3f}, Average token loss: {avg_loss:.3f}")

    optimizer.zero_grad()

    # Create new LoRA step in the evolutionary chain
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Generate next step ID
    model_base_path = f"/lora_models/{model_folder}"
    existing_steps = []
    if os.path.exists(model_base_path):
        for item in os.listdir(model_base_path):
            if item.startswith("step_") and "_from_" in item:
                try:
                    step_num = int(item.split("_")[1])
                    existing_steps.append(step_num)
                except (IndexError, ValueError):
                    continue

    next_step_id = str(max(existing_steps) + 1).zfill(3) if existing_steps else "001"

    current_step = step_folder.split("_")[1] if "_from_" in step_folder and step_folder != "initial" else "initial"
    new_step_folder = f"step_{next_step_id}_from_{current_step}_{timestamp}"
    new_lora_path = f"{model_folder}/{new_step_folder}"
    new_full_path = f"/lora_models/{new_lora_path}"

    # Save updated model
    os.makedirs(new_full_path, exist_ok=True)
    model.save_pretrained(new_full_path)

    # Save training metadata
    training_metadata = {
        "original_lora_path": lora_path,
        "new_lora_path": new_lora_path,
        "model_folder": model_folder,
        "model_id": model_id,
        "parent_step": current_step,
        "step_id": next_step_id,
        "step_folder": new_step_folder,
        "reward_value": reward_value,
        "learning_rate": learning_rate,
        "completion_length": len(completion_text),
        "output_tokens": output_length,
        "tokens_per_update": tokens_per_update,
        "average_token_loss": float(avg_loss),
        "total_loss": float(total_loss),
        "training_timestamp": timestamp,
        "training_method": "token_by_token_grpo",
        "base_model": base_model,
    }

    with open(f"{new_full_path}/training_metadata.json", "w") as f:
        json.dump(training_metadata, f, indent=2)

    print(f"Model updated and saved to {new_lora_path}")

    return {
        "success": True,
        "new_lora_path": new_lora_path,
        "original_lora_path": lora_path,
        "training_metadata": training_metadata,
    }


@app.function(
    image=base_image,
    timeout=300,
    volumes={"/lora_models": lora_vol},
)
def initialize_model_modal(
    base_model: str,
    model_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Initialize a new model with an initial LoRA"""
    model_folder = f"model_{model_id}"
    initial_path = f"{model_folder}/initial"
    full_path = f"/lora_models/{initial_path}"

    # Create the directory structure
    os.makedirs(full_path, exist_ok=True)

    # Create initial metadata
    metadata = {
        "model_id": model_id,
        "base_model": base_model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "step": "initial",
        "kwargs": kwargs,
    }

    with open(f"{full_path}/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Initialized model {model_id} at {initial_path}")

    return {
        "success": True,
        "model_id": model_id,
        "lora_path": initial_path,
        "base_model": base_model,
        "metadata": metadata,
    }


@app.function(
    image=base_image,
    timeout=300,
    volumes={"/lora_models": lora_vol},
)
def fetch_model_modal(model_id: str) -> Dict[str, Any]:
    """Fetch an existing model by ID"""
    model_folder = f"model_{model_id}"
    model_base_path = f"/lora_models/{model_folder}"

    if not os.path.exists(model_base_path):
        return {"success": False, "error": f"Model {model_id} not found"}

    # Find the latest step
    latest_step = "initial"
    latest_step_num = -1

    for item in os.listdir(model_base_path):
        if item.startswith("step_") and "_from_" in item:
            try:
                step_num = int(item.split("_")[1])
                if step_num > latest_step_num:
                    latest_step_num = step_num
                    latest_step = item
            except (IndexError, ValueError):
                continue

    lora_path = f"{model_folder}/{latest_step}"
    metadata_path = f"/lora_models/{lora_path}/model_metadata.json"

    # Load metadata if available
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        # Try to load from training metadata
        training_metadata_path = f"/lora_models/{lora_path}/training_metadata.json"
        if os.path.exists(training_metadata_path):
            with open(training_metadata_path, "r") as f:
                metadata = json.load(f)

    base_model = metadata.get("base_model", DEFAULT_BASE_MODEL)

    return {
        "success": True,
        "model_id": model_id,
        "lora_path": lora_path,
        "base_model": base_model,
        "metadata": metadata,
    }


@app.function(
    image=base_image,
    timeout=300,
    volumes={"/lora_models": lora_vol},
)
def delete_model_modal(model_id: str) -> Dict[str, Any]:
    """Delete a model and all its steps"""
    import shutil
    
    model_folder = f"model_{model_id}"
    model_base_path = f"/lora_models/{model_folder}"

    if not os.path.exists(model_base_path):
        return {"success": False, "error": f"Model {model_id} not found"}

    try:
        shutil.rmtree(model_base_path)
        return {"success": True, "message": f"Model {model_id} deleted successfully"}
    except Exception as e:
        return {"success": False, "error": f"Failed to delete model {model_id}: {str(e)}"}