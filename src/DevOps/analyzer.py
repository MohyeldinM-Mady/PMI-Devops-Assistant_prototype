from src.Reasoning.llm import generate_response


MAX_FILES = 30
MAX_PATCH_PER_FILE = 1000
MAX_TOTAL_PATCH = 12000
MAX_HISTORICAL_CONTEXT = 6000


def _build_changes(files: list[dict]) -> str:
    changes = []
    total_chars = 0

    for file in files[:MAX_FILES]:
        filename = file.get("filename", "unknown")
        status = file.get("status", "unknown")
        patch = file.get("patch") or ""

        remaining = MAX_TOTAL_PATCH - total_chars

        if remaining <= 0:
            break

        patch = patch[:min(MAX_PATCH_PER_FILE, remaining)]
        total_chars += len(patch)

        changes.append(
            f"File: {filename}\n"
            f"Status: {status}\n"
            f"Patch:\n{patch}"
        )

    return "\n\n".join(changes)


def analyze_pull_request(
    files: list[dict],
    historical_context: str,
) -> str:

    print(">>> analyze_pull_request: START", flush=True)

    print(">>> Starting _build_changes", flush=True)
    changes = _build_changes(files)
    print(">>> Finished _build_changes", flush=True)

    historical_context = (
        historical_context or ""
    )[:MAX_HISTORICAL_CONTEXT]

    print(
        f"Files analyzed: {min(len(files), MAX_FILES)}",
        flush=True,
    )
    print(
        f"Current diff size: {len(changes)} characters",
        flush=True,
    )
    print(
        f"Historical context size: {len(historical_context)} characters",
        flush=True,
    )

    prompt = f"""
You are PMI, an AI DevOps assistant reviewing a GitHub Pull Request.

Analyze the current Pull Request using ONLY the provided information.

CURRENT PULL REQUEST:
{changes}

HISTORICAL PROJECT CONTEXT:
{historical_context}

Provide a concise review containing:

1. Confirmed bugs, regressions, security issues, or broken behavior.
2. Recommendations for confirmed issues.
3. Relevant historical context when applicable.

Rules:
- Do not invent facts.
- Do not report hypothetical or speculative issues.
- Only report a finding when it is directly supported by the provided information.
- Do not assume that code is missing just because it is not shown in the diff.
- Do not treat an incomplete diff as evidence that a file is incomplete.
- Ignore minor formatting or style issues.
- If there are no confirmed issues, say "No significant issues found."
- Do not reveal your internal reasoning.
- Keep the final review concise.
- For every finding, include the file path and concrete evidence.

Return only the final review.
"""

    print(">>> Calling generate_response", flush=True)

    analysis = generate_response(prompt)

    print(">>> generate_response returned", flush=True)
    print(
        f"Analysis length: {len(analysis or '')}",
        flush=True,
    )

    return analysis.strip()