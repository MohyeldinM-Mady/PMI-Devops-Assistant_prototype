import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "openrouter/free",
)


@lru_cache(maxsize=1)
def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def generate_response(
    prompt: str,
    *,
    max_tokens: int = 900,
    temperature: float = 0.1,
) -> str:

    print(">>> generate_response START", flush=True)
    print(f">>> Model: {MODEL_NAME}", flush=True)

    response = get_client().chat.completions.create(
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

    print(f"finish_reason: {choice.finish_reason}", flush=True)
    print(
        f"usage: {getattr(response, 'usage', None)}",
        flush=True,
    )

    content = choice.message.content

    if not content:
        print(
            "WARNING: LLM returned an empty response.",
            flush=True,
        )
        return ""

    print(">>> generate_response DONE", flush=True)

    return content.strip()