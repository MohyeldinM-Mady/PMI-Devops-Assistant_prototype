from src.Reasoning.llm import generate_response


MAX_FILES = 10
MAX_PATCH_PER_FILE = 400
MAX_TOTAL_PATCH = 3000
MAX_HISTORICAL_CONTEXT = 1000


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
    Review this GitHub Pull Request using only the provided information.

    CURRENT PR:
    {changes}

    PROJECT CONTEXT:
    {historical_context}

    Report only confirmed bugs, regressions, security issues, or broken behavior.

    Rules:
    - Do not invent facts or speculate.
    - Ignore style issues.
    - Include file path and evidence for each finding.
    - If no confirmed issues exist, say exactly:
    No significant issues found.

    Return only the concise final review.
    """

    print(">>> Calling generate_response", flush=True)

    analysis = generate_response(
        prompt,
        max_tokens=80,
    )

    print(">>> generate_response returned", flush=True)

    print(
        f"Analysis length: {len(analysis or '')}",
        flush=True,
    )

    return analysis.strip()