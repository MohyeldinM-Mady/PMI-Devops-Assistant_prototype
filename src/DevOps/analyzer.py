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

    Analyze the pull request carefully before producing the final review.

    Use ONLY:
    1. The current pull request diff.
    2. The supplied historical project context.

    Do not invent facts or assume information that is not supported by the provided context.

    Reason about:
    - Correctness
    - Potential bugs or regressions
    - Security concerns
    - Maintainability
    - Consistency with the existing project
    - Relevant historical context

    After completing your analysis, provide ONLY the final review.
    Do not expose your internal reasoning or chain-of-thought.

    Return the final review using this structure:

    ## Summary
    Briefly describe what the PR changes.

    ## Findings
    List only concrete issues or risks supported by the diff or historical context.
    If there are no significant issues, explicitly say so.

    ## Recommendations
    Provide practical recommendations when needed.

    CURRENT PULL REQUEST:
    {changes}

    HISTORICAL PROJECT CONTEXT:
    {historical_context or "No relevant historical context was found."}
    """

    analysis = generate_response(
        prompt,
        max_tokens=4096,
        temperature=0.1,
    )

    print(f"Analysis length: {len(analysis or '')}")

    return analysis.strip()