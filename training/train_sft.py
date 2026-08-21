import os
import torch
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not found in .env")
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig


MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

TRAIN_FILE = "training/data/train.jsonl"
VAL_FILE = "training/data/validation.jsonl"

OUTPUT_DIR = "training/output/pmi-qwen-3b"


print("Starting PMI QLoRA training...")
print("CUDA available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("CUDA is not available. Training requires the NVIDIA GPU.")

print("GPU:", torch.cuda.get_device_name(0))


# --------------------------------------------------
# 1. Load datasets
# --------------------------------------------------

print("\nLoading datasets...")

dataset = load_dataset(
    "json",
    data_files={
        "train": TRAIN_FILE,
        "validation": VAL_FILE,
    },
)

print("Training examples:", len(dataset["train"]))
print("Validation examples:", len(dataset["validation"]))


# --------------------------------------------------
# 2. Load tokenizer
# --------------------------------------------------

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    token=HF_TOKEN,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# --------------------------------------------------
# 3. 4-bit quantization
# --------------------------------------------------

print("\nConfiguring 4-bit quantization...")

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)


# --------------------------------------------------
# 4. Load Qwen
# --------------------------------------------------

print("\nLoading Qwen 2.5 3B in 4-bit...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=quant_config,
    device_map="auto",
    torch_dtype=torch.float16,
    token=HF_TOKEN,
)

model.config.use_cache = False

print("Model loaded.")
print("Model dtype:", next(model.parameters()).dtype)


# --------------------------------------------------
# 5. LoRA configuration
# --------------------------------------------------

print("\nConfiguring LoRA...")

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,

    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],

    bias="none",
    task_type="CAUSAL_LM",
)


# --------------------------------------------------
# 6. Training configuration
# --------------------------------------------------

training_args = SFTConfig(
    output_dir=OUTPUT_DIR,

    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,

    num_train_epochs=3,
    learning_rate=2e-4,

    fp16=False,
    bf16=False,

    gradient_checkpointing=True,

    # Disable gradient clipping
    max_grad_norm=0.0,

    logging_steps=5,

    eval_strategy="steps",
    eval_steps=25,

    save_strategy="steps",
    save_steps=25,
    save_total_limit=2,

    optim="paged_adamw_8bit",

    remove_unused_columns=False,
    report_to="none",

    max_length=512,
)
# --------------------------------------------------
# 7. Create trainer
# --------------------------------------------------

print("\nCreating SFT trainer...")

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    processing_class=tokenizer,
    peft_config=lora_config,
)

# --------------------------------------------------
# 8. Train
# --------------------------------------------------

print("\nStarting training...")
print("Keep the laptop plugged in.")
print("Do not close this terminal.")

trainer.train()


# --------------------------------------------------
# 9. Save adapter
# --------------------------------------------------

print("\nSaving PMI LoRA adapter...")

trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\nTraining complete!")
print("Adapter saved to:", OUTPUT_DIR)