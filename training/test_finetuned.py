import os
import torch

from dotenv import load_dotenv
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not found in .env")

BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_PATH = "baherrr/pmi-qwen-3b"


print("Loading PMI fine-tuned model...")

print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))


quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)


print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=HF_TOKEN,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


print("\nLoading base Qwen model...")

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=quant_config,
    device_map="auto",
    torch_dtype=torch.float16,
    token=HF_TOKEN,
)

print("Base model loaded.")


print("\nLoading PMI LoRA adapter...")

model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_PATH,
    token=HF_TOKEN,
)

model.eval()

print("PMI adapter loaded successfully!")


def ask_pmi(question):
    messages = [
        {
            "role": "system",
            "content": (
                "You are PMI, an AI DevOps project knowledge assistant. "
                "Answer using only the provided project information. "
                "Do not invent project facts."
            ),
        },
        {
            "role": "user",
            "content": question,
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
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=False,
        )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )

    return response.strip()


questions = [
    "What files were affected by the change 'chore: update project dependencies'?",
    "What happened in commit d1504d9d?",
    "What was added in pull request 15?",
    "Why was the FastAPI /chat endpoint added?",
    "What should PMI do if there is not enough information to determine the cause of a bug?",
]


print("\n========================================")
print("PMI FINE-TUNED MODEL TEST")
print("========================================")

for i, question in enumerate(questions, start=1):
    print(f"\n--- Test {i} ---")
    print("Question:", question)

    answer = ask_pmi(question)

    print("PMI:", answer)


print("\n========================================")
print("Testing complete!")
print("========================================")