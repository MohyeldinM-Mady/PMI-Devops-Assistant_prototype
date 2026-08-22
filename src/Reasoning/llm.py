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

MAX_INPUT_TOKENS = 1024


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
# Base model
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
# Download PMI LoRA adapter
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
# Load LoRA adapter
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

def generate_response(prompt, max_tokens=50):

    print(">>> generate_response START", flush=True)

    messages = [
        {
            "role": "system",
            "content": (
                "You are PMI, an AI DevOps assistant. "
                "Return only a concise final review. "
                "Never reproduce the input code or patch."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    print(">>> Applying chat template", flush=True)

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    print(">>> Tokenizing", flush=True)

    # IMPORTANT:
    # The prompt must already be small enough.
    # Do not silently truncate the end of the instructions.
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=False,
    )

    input_token_count = inputs["input_ids"].shape[1]

    print(
        f">>> Input tokens: {input_token_count}",
        flush=True,
    )

    if input_token_count > MAX_INPUT_TOKENS:
        raise ValueError(
            f"Prompt is too large: {input_token_count} tokens "
            f"(max allowed: {MAX_INPUT_TOKENS})"
        )

    print(
        f">>> Model device: {model.device}",
        flush=True,
    )

    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    print(">>> Starting model.generate()", flush=True)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            use_cache=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.05,
        )

    print(">>> model.generate() FINISHED", flush=True)

    generated_tokens = outputs[0][
        inputs["input_ids"].shape[1]:
    ]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    print(">>> RAW MODEL RESPONSE:", flush=True)
    print(repr(response), flush=True)
    print(">>> END RAW MODEL RESPONSE", flush=True)

    return response.strip()