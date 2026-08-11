from src.Reasoning.llm import generate_response


def analyze_pull_request(
    files: list[dict],
    historical_context: str,
) -> str:
    changes = []

    for file in files:
        changes.append(
            f"File: {file['filename']}\n"
            f"Status: {file['status']}\n"
            f"Patch:\n{file['patch']}"
        )

    prompt = f"""
You are PMI, an AI DevOps assistant reviewing a GitHub Pull Request.

Analyze the current Pull Request using ONLY the provided information.

CURRENT PULL REQUEST:
{"\n\n".join(changes)}

HISTORICAL PROJECT CONTEXT:
{historical_context}

Provide a concise review containing:

1. Potential risks or warnings.
2. Recommendations for the developer.
3. Relevant historical context when applicable.

Do not invent facts that are not present in the provided context.
If there are no meaningful risks, say so clearly.
"""

    return generate_response(prompt)