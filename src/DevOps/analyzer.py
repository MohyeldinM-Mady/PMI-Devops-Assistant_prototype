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
    You are PMI, an AI code reviewer analyzing a GitHub Pull Request.

    Analyze the PR using ONLY the current diff and the historical project context.

    Your priority is ACCURACY. Do not invent or assume anything.

    Rules:
    - Report only issues that are directly supported by the provided evidence.
    - Do not assume code is missing because it is not visible in a diff.
    - Do not claim that a function, endpoint, import, file, or dependency is missing unless the provided context proves it.
    - Do not treat a truncated diff as a truncated source file.
    - Do not report hypothetical problems as confirmed bugs.
    - Do not report formatting or minor style issues.
    - If an issue cannot be verified, do not report it.
    - Prefer "No significant issues found" over a speculative finding.
    - Do not reveal your internal reasoning.

    Focus on:
    - Bugs and regressions
    - Security issues
    - Incorrect behavior
    - Broken integrations
    - Problems introduced by this PR

    For every finding, provide:
    - Severity
    - File
    - Evidence
    - Impact

    CURRENT PR DIFF:
    {changes}

    HISTORICAL CONTEXT:
    {historical_context or "No relevant historical context."}

    Return ONLY:

    ## Summary
    Brief summary of the PR.

    ## Findings
    Confirmed issues only.

    ## Recommendations
    Actionable recommendations for confirmed issues.

    If there are no confirmed issues, say:
    "No significant issues found."
    """

    analysis = generate_response(
        prompt,
        max_tokens=4096,
        temperature=0.1,
    )

    print(f"Analysis length: {len(analysis or '')}")

    return analysis.strip()