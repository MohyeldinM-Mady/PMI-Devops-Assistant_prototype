


import os
import torch

from dotenv import load_dotenv
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel
from huggingface_hub import snapshot_download


# ============================================================
# Configuration
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

print("HF_TOKEN loaded:", HF_TOKEN is not None)

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not found in .env")


BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_PATH = "baherrr/pmi-qwen-3b"


# ============================================================
# GPU
# ============================================================

print("Loading PMI model...")
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))


# ============================================================
# 4-bit configuration
# ============================================================

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)


# ============================================================
# Tokenizer
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=HF_TOKEN,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# ============================================================
# Base Qwen model
# ============================================================

print("\nLoading Qwen 2.5 3B...")

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=quant_config,
    device_map="auto",
    dtype=torch.float16,
    token=HF_TOKEN,
)

print("Base model loaded.")


# ============================================================
# Download PMI LoRA adapter locally
# ============================================================

print("\nLoading PMI fine-tuned adapter...")
print("Adapter:", ADAPTER_PATH)

adapter_local_path = snapshot_download(
    repo_id=ADAPTER_PATH,
    repo_type="model",
    token=HF_TOKEN,
)

print("Adapter downloaded to:")
print(adapter_local_path)


# ============================================================
# Load PMI LoRA adapter
# ============================================================

model = PeftModel.from_pretrained(
    base_model,
    adapter_local_path,
    is_trainable=False,
)

model.eval()

print("PMI adapter loaded successfully!")


# ============================================================
# Generation
# ============================================================

def generate_response(prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are PMI, an AI project assistant. "
                "Answer the user's question using only the provided "
                "project context. Do not invent project information."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        text,
        return_tensors="pt",
    )

    # Put inputs on the same device as the model
    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )

    return response.strip()
