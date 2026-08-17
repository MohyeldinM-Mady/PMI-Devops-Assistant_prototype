import os
from functools import lru_cache

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "openai/gpt-oss-20b:groq",
)


@lru_cache(maxsize=1)
def get_client():
    token = os.getenv("HF_TOKEN")

    if not token:
        raise RuntimeError("HF_TOKEN is not configured.")

    return InferenceClient(api_key=token)


def generate_response(
    prompt: str,
    *,
    max_tokens: int = 4096,
    temperature: float = 0.1,
) -> str:

    response = get_client().chat_completion(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    choice = response.choices[0]

    print(f"finish_reason: {choice.finish_reason}")
    print(f"usage: {getattr(response, 'usage', None)}")

    content = choice.message.content

    if not content:
        print("WARNING: LLM returned an empty response.")
        return ""

    return content.strip()