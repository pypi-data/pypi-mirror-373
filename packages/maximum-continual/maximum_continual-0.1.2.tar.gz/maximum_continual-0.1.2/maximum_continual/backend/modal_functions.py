"""
Modal Functions for Maximum Continual Training

Contains all Modal app functions that run on Modal's cloud infrastructure.
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple
import modal
import json
from typing import Any
import aiohttp
import modal
from abc import ABC, abstractmethod
from pydantic import BaseModel
from tqdm.auto import tqdm

class LoraInfoT(BaseModel):
    step: int
    full_lora_path: str
    base_model: str
    model_id: str
    timestamp: str


# Default base model
# DEFAULT_BASE_MODEL = "Qwen/Qwen3-14B"
DEFAULT_BASE_MODEL = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
DEFAULT_BASE_MODEL = "openai/gpt-oss-20b"
# Modal app for generic continual learning
app = modal.App("maximum-continual")

# Modal volume for storing LoRA models
lora_vol = modal.Volume.from_name("continual-lora-models-v3", create_if_missing=True)

LORA_PATH = "/lora_models"



class AbstractModelInfoBackend(ABC):
    @abstractmethod
    def fetch_current_step(self) -> LoraInfoT | None:
        pass
    
    @abstractmethod
    def fetch_next_step(self) -> LoraInfoT | None:
        pass
    
    @abstractmethod
    def update_current_step(self, lora_info: LoraInfoT) -> LoraInfoT | None:
        pass





class ModalModelInfoBackend(AbstractModelInfoBackend):
    def __init__(self, model_id: str, lora_vol_path: str):
        self.model_id = model_id
        self.lora_vol_path = lora_vol_path
    def _format_new_step_folder(self, next_step_id: str, current_step: int, timestamp: str) -> str:
        return f"step_{next_step_id}_from_{current_step}"
    
    def _get_step_id_from_file_name(self, file_name: str) -> int | None:
        if file_name.startswith("step_") and "_from_" in file_name:
            try:
                return int(file_name.split("_")[1])
            except (IndexError, ValueError):
                return None
        return None

    def fetch_current_step(self) -> LoraInfoT | None:
        model_base_path = f"{self.lora_vol_path}/{self.model_id}"
        print(f"Fetching model {self.model_id} from {model_base_path}")
        if not os.path.exists(model_base_path):
            return None

        latest_step_num, full_lora_path = self._fetch_max_step_and_lora_path()

        
        metadata_path = f"{full_lora_path}/model_metadata.json"

        # Load metadata if available
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        else:
            return None

        base_model = metadata.get("base_model", DEFAULT_BASE_MODEL)
        timestamp = metadata.get("timestamp", None)
        latest_lora_info = LoraInfoT(
            step=latest_step_num,
            full_lora_path=full_lora_path,
            base_model=base_model,
            model_id=self.model_id,
            timestamp=timestamp,
        )
        return latest_lora_info
    
    def _fetch_max_step_and_lora_path(self) -> Tuple[int, str] | None:
        # Find the latest step
        latest_step = None
        latest_step_num = -1
        model_base_path = f"{self.lora_vol_path}/{self.model_id}"
        for item in os.listdir(model_base_path):
            print(item)
            if (step_id := self._get_step_id_from_file_name(item)) is not None:
                try:
                    step_num = step_id
                    if step_num > latest_step_num:
                        latest_step_num = step_num
                        latest_step = item
                except (IndexError, ValueError):
                    continue
        lora_path = f"{self.lora_vol_path}/{self.model_id}/{latest_step}"
        return latest_step_num, lora_path
        
    def fetch_next_step(self) -> LoraInfoT | None:
        lora_info = self.fetch_current_step()
        if lora_info is None:
            return None
        # Create new LoRA step in the evolutionary chain
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        current_max_step, _ = self._fetch_max_step_and_lora_path()
        
        next_step_id = current_max_step + 1
        new_step_folder = self._format_new_step_folder(next_step_id, lora_info.step, timestamp)
        new_full_path = f"{self.lora_vol_path}/{self.model_id}/{new_step_folder}"

        return LoraInfoT(
            step=current_max_step + 1,
            full_lora_path=new_full_path,
            lora_name=new_step_folder,
            base_model=lora_info.base_model,
            model_id=lora_info.model_id,
            timestamp=timestamp,
        )

    def update_current_step(self, lora_info: LoraInfoT) -> LoraInfoT | None:
        new_full_path = lora_info.full_lora_path
        os.makedirs(new_full_path, exist_ok=True)
        with open(f"{new_full_path}/model_metadata.json", "w") as f:
            json.dump(lora_info.model_dump(), f, indent=2)
        return lora_info

def install_dependencies():
    """Install the base model dependencies"""
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
    _ = AutoModelForCausalLM.from_pretrained(DEFAULT_BASE_MODEL, trust_remote_code=True)
    _ = AutoTokenizer.from_pretrained(DEFAULT_BASE_MODEL, trust_remote_code=True)


# Modal image with dependencies
base_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("transformers>=4.35.0", "torch>=2.6.0", "pydantic>=2.10.0",  "peft>=0.7.0",
        "bitsandbytes>=0.41.0", 
        "accelerate>=0.24.0",
        "datasets>=2.14.0",
        "tqdm>=4.65.0",
        "requests>=2.31.0",
        "pandas>=2.1.0",)
    .run_function(install_dependencies, gpu="H100")
    .apt_install("git", "wget")
    .pip_install("pydantic>=2.10.0")
    .run_commands("""ls && \
wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb && \
dpkg -i cuda-keyring_1.1-1_all.deb && \
apt-get update && \
apt-get install -y cuda-toolkit-12-8
""", gpu="H100").pip_install("deepspeed","mpi4py", gpu="H100")
)


@app.function(
    image=base_image,
    gpu="A100",
    timeout=3600,
    volumes={LORA_PATH: lora_vol},
    max_containers=2,
)
def generate_prediction_modal(
    messages: List[Dict[str, str]],
    model_id: str,
    max_new_tokens: int = 2048,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> Dict[str, Any]:
    """Generate a prediction using the LoRA model"""
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  # type: ignore
    from peft import PeftModel  # type: ignore
    lora_info = ModalModelInfoBackend().fetch_lora_info(model_id)
    if lora_info is None:
        raise ValueError(f"Model {model_id} not found")
    # Load base model
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
    )

    base_model_instance = AutoModelForCausalLM.from_pretrained(
        lora_info.base_model,
        device_map="auto", 
        quantization_config=bnb_config,
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(lora_info.base_model, trust_remote_code=True)

    # Load LoRA adapter if it exists
    full_lora_path = lora_info.full_lora_path
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

    # Use apply_chat_template to format messages
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "prediction": generated_text,
        "full_response": generated_text,
        "lora_path": lora_info.full_lora_path,
        "base_model": lora_info.base_model,
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
    gpu="H100", 
    timeout=3600,
    volumes={LORA_PATH: lora_vol},
    max_containers=2,
)
def update_model_modal(
    messages: List[Dict[str, str]],  # Changed from completion_text to messages
    reward_value: float,
    model_id: str,
    learning_rate: float = 2e-5,
) -> Dict[str, Any]:
    """Update a LoRA model with reward feedback using chat template"""
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  # type: ignore
    from peft import PeftModel, LoraConfig, get_peft_model, TaskType  # type: ignore
    model_info_backend = ModalModelInfoBackend(model_id, lora_vol_path=LORA_PATH)
    lora_info = model_info_backend.fetch_current_step()
    if lora_info is None:
        raise ValueError(f"Model {model_id} not found")
    base_model = lora_info.base_model
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
    full_lora_path = lora_info.full_lora_path

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
            r=32,
            lora_alpha=32,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                # Removed MLP modules for VLLM compatibility
                # "gate_proj", "up_proj", "down_proj",
            ],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        model = get_peft_model(base_model_instance, lora_config)
        print(f"Created new LoRA model for: {lora_info.lora_name}")

    print("Enabling gradient checkpointing...")
    if hasattr(model, 'gradient_checkpointing_enable'):
        model.gradient_checkpointing_enable()

    # Prepare model for training
    model.train()

    # Create optimizer for trainable parameters
    trainable_params = [p for n, p in model.named_parameters() if p.requires_grad]
    print(f"Found {len(trainable_params)} trainable parameters")

    if not trainable_params:
        raise ValueError("No trainable parameters found in the model")

    optimizer = torch.optim.AdamW(trainable_params, lr=learning_rate)

    # Use apply_chat_template to format messages for training
    formatted_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False
    )
    
    # Tokenize the formatted text for training
    inputs = tokenizer(
        formatted_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
    ).to(model.device)

    label_ids = inputs["input_ids"]
    output_length = label_ids.shape[1] - 1

    print(f"Training on chat template with {output_length} tokens, reward: {reward_value:.3f}")

    # Token-by-token training with reward weighting
    total_loss = 0.0
    tokens_per_update = 512

    device = next(model.parameters()).device if hasattr(model, 'parameters') else 'cuda'
    reward_tensor = torch.ones(output_length, device=device, requires_grad=True) * reward_value

    for i in tqdm(range(0, output_length, tokens_per_update)):
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
    new_lora_info = model_info_backend.fetch_next_step()
    if new_lora_info is None:
        raise ValueError(f"Failed to create new LoRA step for model {model_id}")
    new_full_path = new_lora_info.full_lora_path
    # Save updated model
    model_info_backend.update_current_step(new_lora_info)
    model.save_pretrained(new_full_path)

    # Save training metadata
    training_metadata = {
        "original_lora_path": lora_info.full_lora_path,
        "new_lora_path": new_lora_info.full_lora_path,
        "model_id": model_id,
        "parent_step": lora_info.step,
        "step_id": new_lora_info.step,
        "reward_value": reward_value,
        "learning_rate": learning_rate,
        "messages_count": len(messages),
        "formatted_text_length": len(formatted_text),
        "output_tokens": output_length,
        "tokens_per_update": tokens_per_update,
        "average_token_loss": float(avg_loss),
        "total_loss": float(total_loss),
        "training_timestamp":new_lora_info.timestamp,
        "training_method": "token_by_token_grpo_chat_template",
        "base_model": base_model,
    }

    with open(f"{new_full_path}/training_metadata.json", "w") as f:
        json.dump(training_metadata, f, indent=2)

    print(f"Model updated and saved to {new_full_path}")

    return new_lora_info.model_dump()

@app.function(
    image=base_image.pip_install("deepspeed", gpu="H100"),
    gpu="H100", 
    timeout=3600,
    volumes={LORA_PATH: lora_vol},
    max_containers=2,
)
def update_model_modal_batch(
    batch_messages: List[Tuple[List[Dict[str, str]], float]],  # 2D list: [conversation][message]
    model_id: str,
    learning_rate: float = 2e-5,
    use_deepspeed: bool = False,
) -> Dict[str, Any]:
    """Efficient batch training with DeepSpeed optimization"""
    import torch
    import deepspeed
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Trainer, TrainingArguments
    from peft import PeftModel, LoraConfig, get_peft_model, TaskType
    from torch.utils.data import Dataset
    import json
    import os
    model_info_backend = ModalModelInfoBackend(model_id, lora_vol_path=LORA_PATH)
    # Custom dataset for reward-weighted training
    class RewardWeightedDataset(Dataset):
        def __init__(self, batch_messages, tokenizer, max_length=2048):
            self.data = []
            for messages, reward in batch_messages:
                formatted_text = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=False
                )
                tokenized = tokenizer(
                    formatted_text,
                    truncation=True,
                    max_length=max_length,
                    padding=False,
                    return_tensors="pt"
                )
                self.data.append({
                    'input_ids': tokenized['input_ids'].squeeze(),
                    'attention_mask': tokenized['attention_mask'].squeeze(),
                    'reward': reward,
                    'length': tokenized['input_ids'].shape[1]
                })
        
        def __len__(self):
            return len(self.data)
        
        def __getitem__(self, idx):
            return self.data[idx]
    

    
    # Custom trainer with reward-weighted loss
    class RewardWeightedTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            labels = inputs.get("labels")
            rewards = inputs.get("rewards")
            
            # Ensure rewards tensor is on the right device and has gradients enabled
            if rewards is not None:
                device = next(model.parameters()).device
                rewards = rewards.to(device).detach()  # Detach rewards to avoid gradient issues
            
            outputs = model(**{k: v for k, v in inputs.items() if k not in ['rewards']})
            
            if labels is not None:
                shift_logits = outputs.logits[..., :-1, :].contiguous()
                shift_labels = labels[..., 1:].contiguous()
                
                # Compute per-token loss
                loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
                token_losses = loss_fct(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1)
                ).view(shift_labels.size())  # [batch_size, seq_len-1]
                
                # Apply reward weighting
                if rewards is not None:
                    # Expand rewards to match token dimensions
                    reward_weights = rewards.unsqueeze(1).expand_as(token_losses).detach()
                    weighted_losses = token_losses * reward_weights
                else:
                    weighted_losses = token_losses
                
                # Mask out padded tokens
                attention_mask = inputs.get('attention_mask')
                if attention_mask is not None:
                    mask = attention_mask[..., 1:].float()  # Shift mask to match labels
                    weighted_losses = weighted_losses * mask
                    valid_tokens = mask.sum()
                    if valid_tokens > 0:
                        loss = weighted_losses.sum() / valid_tokens
                    else:
                        loss = weighted_losses.sum()  # Fallback if no valid tokens
                else:
                    loss = weighted_losses.mean()
                
                # Debug: Check if loss requires grad
                if not loss.requires_grad:
                    print(f"WARNING: Loss does not require gradients! Loss shape: {loss.shape}")
                    print(f"Model has trainable params: {any(p.requires_grad for p in model.parameters())}")
                
            else:
                loss = outputs.loss

            return (loss, outputs) if return_outputs else loss

    # Load model and tokenizer
    lora_info = model_info_backend.fetch_current_step()
    if lora_info is None:
        raise ValueError(f"Model {model_id} not found")
    
    base_model = lora_info.base_model
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # Custom data collator for reward weighting
    def reward_weighted_collate_fn(batch):
        # Pad sequences to same length
        max_len = max(item['length'] for item in batch)
        
        input_ids = []
        attention_masks = []
        rewards = []
        
        for item in batch:
            # Pad input_ids and attention_mask
            pad_length = max_len - item['length']
            if pad_length > 0:
                input_ids.append(torch.cat([
                    item['input_ids'], 
                    torch.full((pad_length,), tokenizer.pad_token_id)
                ]))
                attention_masks.append(torch.cat([
                    item['attention_mask'],
                    torch.zeros(pad_length)
                ]))
            else:
                input_ids.append(item['input_ids'])
                attention_masks.append(item['attention_mask'])
            
            rewards.append(item['reward'])
        
        return {
            'input_ids': torch.stack(input_ids),
            'attention_mask': torch.stack(attention_masks),
            'labels': torch.stack(input_ids),  # For causal LM, labels = input_ids
            'rewards': torch.tensor(rewards, dtype=torch.float32)
        }

    # Load model with more efficient configuration for DeepSpeed
    if use_deepspeed:
        # Don't use BitsAndBytesConfig with DeepSpeed - they conflict
        base_model_instance = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,  # Use fp16 for DeepSpeed
            trust_remote_code=True,
        )
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True, 
            bnb_4bit_compute_dtype=torch.float16
        )
        base_model_instance = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map="auto",
            quantization_config=bnb_config,
            trust_remote_code=True,
        )
    if hasattr(base_model_instance, "enable_input_require_grads"):
        base_model_instance.enable_input_require_grads()
    else:
        def make_inputs_require_grad(module, input, output):
            output.requires_grad_(True)

        base_model_instance.get_input_embeddings().register_forward_hook(make_inputs_require_grad)
    # Load or create LoRA
    full_lora_path = lora_info.full_lora_path
    if os.path.exists(full_lora_path):
        model = PeftModel.from_pretrained(base_model_instance, full_lora_path)
        print(f"Loaded LoRA from: {full_lora_path}")
    else:
        lora_config = LoraConfig(
            r=32,
            lora_alpha=32,
            target_modules="all-linear",
            target_parameters=[
                "7.mlp.experts.gate_up_proj",
                "7.mlp.experts.down_proj",
                "15.mlp.experts.gate_up_proj",
                "15.mlp.experts.down_proj",
                "23.mlp.experts.gate_up_proj",
                "23.mlp.experts.down_proj",
            ],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        model = get_peft_model(base_model_instance, lora_config)
        print(f"Created new LoRA model: {lora_info.lora_name}")
        print(f"LoRA target modules (VLLM-compatible): {lora_config.target_modules}")

    # Ensure model is in training mode and LoRA parameters require gradients
    model.train()
    

    # Prepare dataset
    dataset = RewardWeightedDataset(batch_messages, tokenizer)
    
    # DeepSpeed configuration
    if use_deepspeed:
        deepspeed_config = {
            "fp16": {
                "enabled": True
            },
            "zero_optimization": {
                "stage": 2,  # ZeRO-2 for memory optimization
                "offload_optimizer": {
                    "device": "cpu",
                    "pin_memory": True
                },
                "allgather_partitions": True,
                "allgather_bucket_size": 2e8,
                "overlap_comm": True,
                "reduce_scatter": True,
                "reduce_bucket_size": 2e8,
                "contiguous_gradients": True
            },
            "train_batch_size": len(batch_messages),
            "train_micro_batch_size_per_gpu": min(4, len(batch_messages)),
            "gradient_accumulation_steps": max(1, len(batch_messages) // 4),
            "wall_clock_breakdown": False
        }
    else:
        deepspeed_config = None

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./tmp_training",
        num_train_epochs=1,
        per_device_train_batch_size=min(4, len(batch_messages)),
        gradient_accumulation_steps=max(1, len(batch_messages) // 4),
        learning_rate=learning_rate,
        warmup_steps=0,
        logging_steps=1,
        save_steps=10,
        save_total_limit=0,
        prediction_loss_only=True,
        remove_unused_columns=False,
        dataloader_drop_last=False,
        fp16=use_deepspeed,  # Use fp16 with DeepSpeed
        gradient_checkpointing=True,
        deepspeed=deepspeed_config if use_deepspeed else None,
        report_to=None,  # Disable wandb/tensorboard
    )

    # Initialize trainer
    trainer = RewardWeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=reward_weighted_collate_fn,
        tokenizer=tokenizer,
    )

    # Train
    print(f"Training on {len(batch_messages)} conversations")
    trainer.train()

    # Create new LoRA step
    new_lora_info = model_info_backend.fetch_next_step()
    if new_lora_info is None:
        raise ValueError(f"Failed to create new LoRA step for model {model_id}")
    model_info_backend.update_current_step(new_lora_info)
    new_full_path = new_lora_info.full_lora_path
    
    # Save the model
    model.save_pretrained(new_full_path)
    
    # Calculate some metrics for metadata  
    total_tokens = sum(len(tokenizer.apply_chat_template(msgs, tokenize=True)) 
                      for msgs, _ in batch_messages)
    batch_rewards = [reward for _, reward in batch_messages]
    avg_reward = sum(batch_rewards) / len(batch_rewards)
    
    # Save training metadata
    training_metadata = {
        "original_lora_path": lora_info.full_lora_path,
        "new_lora_path": new_lora_info.full_lora_path,
        "model_folder": lora_info.lora_name,
        "model_id": model_id,
        "parent_step": lora_info.step,
        "step_id": new_lora_info.step,
        "step_folder": new_lora_info.lora_name,
        "batch_size": len(batch_messages),
        "rewards": batch_rewards,
        "average_reward": avg_reward,
        "learning_rate": learning_rate,
        "total_tokens": total_tokens,
        "training_timestamp": new_lora_info.timestamp,
        "training_method": "batch_reward_weighted_deepspeed" if use_deepspeed else "batch_reward_weighted",
        "base_model": base_model,
        "use_deepspeed": use_deepspeed,
    }

    with open(f"{new_full_path}/training_metadata.json", "w") as f:
        json.dump(training_metadata, f, indent=2)

    print(f"Batch training completed. Model saved to {new_full_path}")
    return new_lora_info.model_dump()


@app.function(
    image=base_image,
    timeout=300,
    volumes={LORA_PATH: lora_vol},
)
def initialize_model_modal(
    base_model: str,
    model_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Initialize a new model with an initial LoRA"""
    model_folder = f"model_{model_id}"
    initial_path = f"{model_folder}/initial"
    full_path = f"{LORA_PATH}/{initial_path}"
    # Create the directory structure
    os.makedirs(full_path, exist_ok=True)
    lora_info = LoraInfoT(
        step=0,
        full_lora_path=initial_path,
        lora_name=model_folder,
        base_model=base_model,
        model_id=model_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    # Create initial metadata
    metadata = lora_info.model_dump()
    with open(f"{full_path}/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Initialized model {model_id} at {initial_path}")
    return lora_info.model_dump()


@app.function(
    image=base_image,
    timeout=300,
    volumes={LORA_PATH: lora_vol},
)
def fetch_model_modal(model_id: str) -> Dict[str, Any] | None:
    """Fetch an existing model by ID"""
    model_info_backend = ModalModelInfoBackend(model_id, lora_vol_path=LORA_PATH)
    latest_lora_info = model_info_backend.fetch_current_step()
    if latest_lora_info is None:
        return None
    return latest_lora_info.model_dump()


@app.function(
    image=base_image,
    timeout=300,
    volumes={"/lora_models": lora_vol},
)
def delete_model_modal(model_id: str):
    """Delete a model and all its steps"""
    import shutil
    
    model_folder = f"model_{model_id}"
    model_base_path = f"/lora_models/{model_folder}"

    if not os.path.exists(model_base_path):
        raise ValueError(f"Model {model_id} not found")

    shutil.rmtree(model_base_path)


N_GPU = 4
GPU_TYPE = "H100"
GPUS_USED =f"{GPU_TYPE}:{N_GPU}"
def install_vllm_dependencies():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    model_name = DEFAULT_BASE_MODEL
    _ = AutoTokenizer.from_pretrained(model_name)
    _ = AutoModelForCausalLM.from_pretrained(model_name)
hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)
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
    import os
    assert os.path.exists("/lora_models/model_test_model/step_003_from_3/adapter_config.json"), f"Adapter config not found at /lora_models/model_test_model/step_003_from_3/adapter_config.json"
    cmd = [
        "vllm",
        "serve",
        "--uvicorn-log-level=info",
        DEFAULT_BASE_MODEL,
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--enable-auto-tool-choice",
        "--tool-call-parser", "hermes",
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
def test_lora():
    web_url = serve.get_web_url()
    print(web_url)
    import requests
    assert os.path.exists("/lora_models/model_test_model/step_003_from_3/adapter_config.json"), f"Adapter config not found at /lora_models/model_test_model/step_003_from_3/adapter_config.json"

    response = requests.post(f"{web_url}/v1/load_lora_adapter", json={"lora_name": "sql_adapter", "lora_path": "/lora_models/model_test_model/step_003_from_3/"})
    print(response.text)
    # from huggingface_hub import snapshot_download
    # import os
    # from vllm import LLM, SamplingParams
    # from vllm.lora.request import LoRARequest
    # os.makedirs("/lora_models/test_lora", exist_ok=True)
    # sql_lora_path = "/lora_models/model_test_model/step_003_from_3/"
    # print(sql_lora_path)
    # lora_request = LoRARequest("sql_adapter", 1, sql_lora_path)
    

    # llm = LLM(model=DEFAULT_BASE_MODEL, enable_lora=True)
    # sampling_params = SamplingParams(
    #     temperature=0,
    #     max_tokens=256,
    #     stop=["[/assistant]"]
    # )

    # prompts = [
    #     "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_74 (icao VARCHAR, airport VARCHAR)\n\n question: Name the ICAO for lilongwe international airport [/user] [assistant]",
    #     "[user] Write a SQL query to answer the question based on the table schema.\n\n context: CREATE TABLE table_name_11 (nationality VARCHAR, elector VARCHAR)\n\n question: When Anchero Pantaleone was the elector what is under nationality? [/user] [assistant]",
    # ]

    # outputs = llm.generate(
    #     prompts,
    #     sampling_params,
    #     lora_request=LoRARequest("sql_adapter", 1, sql_lora_path)
    # )
    # print(outputs)

@app.local_entrypoint()
def test_lora_local():
    test_lora.remote()
