from src.Reasoning.llm import generate_response


MAX_FILES = 30
MAX_PATCH_PER_FILE = 2500
MAX_TOTAL_PATCH = 30000


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
    changes = _build_changes(files)

    print(f"Files analyzed: {min(len(files), MAX_FILES)}")
    print(f"Current diff size: {len(changes)} characters")
    print(f"Historical context size: {len(historical_context or '')} characters")

    prompt = f"""
    You are PMI, an AI DevOps assistant reviewing a GitHub Pull Request.

    Analyze the PR using only the provided diff and historical context.

    Focus ONLY on real bugs, regressions, security issues, or broken behavior
    introduced by this PR.

    Rules:
    - Do not guess.
    - Do not invent missing code or functionality.
    - Do not assume code is missing because it is not shown in the diff.
    - Only report issues supported by concrete evidence.
    - Ignore formatting and minor style issues.
    - If no real issue is found, say "No significant issues found."
    - Do not reveal your internal reasoning.

    Keep the final review concise.

    CURRENT PR DIFF:
    {changes}

    HISTORICAL CONTEXT:
    {historical_context or "No relevant historical context."}

    Return:

    ## Summary
    One or two sentences.

    ## Findings
    Only confirmed issues, with file and evidence.

    ## Recommendations
    Only recommendations related to confirmed issues.
    """

    analysis = generate_response(
        prompt,
        max_tokens=4096,
        temperature=0.1,
    )

    print(f"Analysis length: {len(analysis or '')}")

    return analysis.strip()