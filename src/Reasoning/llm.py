import os
from functools import lru_cache

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

MODEL_NAME = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-3B-Instruct")


@lru_cache(maxsize=1)
def get_client():
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is not configured.")
    return InferenceClient(api_key=token)


def generate_response(
    prompt: str,
    *,
    max_tokens: int = 900,
    temperature: float = 0.1,
) -> str:
    response = get_client().chat_completion(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""
