import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

print("HF token loaded:", bool(os.getenv("HF_TOKEN")))
print("LLM model:", os.getenv("LLM_MODEL"))

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "Qwen/Qwen2.5-3B-Instruct"
)

client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)


def generate_response(prompt: str) -> str:
    response = client.chat_completion(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=4096,
        temperature=0.2,
    )

    print("=== HF RAW RESPONSE ===")
    print(repr(response))

    print("=== CHOICES ===")
    print(repr(response.choices))

    if response.choices:
        print("=== MESSAGE ===")
        print(repr(response.choices[0].message))

    return response.choices[0].message.content or ""