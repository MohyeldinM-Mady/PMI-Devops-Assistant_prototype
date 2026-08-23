from src.Reasoning.llm import generate_response


MAX_FILES = 10
MAX_PATCH_PER_FILE = 1500
MAX_TOTAL_PATCH = 12000
MAX_HISTORICAL_CONTEXT = 2000


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
    You are reviewing a GitHub Pull Request.

    Review ONLY the provided pull request changes and project context.

    IMPORTANT:
    - Return ONLY the final PR review.
    - Do NOT explain your reasoning or thinking process.
    - Do NOT describe how you analyzed the pull request.
    - Do NOT summarize every changed file.
    - Do NOT repeat the pull request contents.
    - Do NOT speculate or make assumptions.
    - Do NOT use phrases such as:
    "Let's examine"
    "We are given"
    "We need to"
    "I should"
    "Let's look at"
    "We can assume"
    "However, we need to check"

    Report ONLY confirmed bugs, regressions, security issues,
    or broken behavior directly supported by the provided information.

    A finding must:
    - Be a confirmed issue.
    - Have explicit evidence in the PR changes or project context.
    - Include the affected file path.

    Do NOT report:
    - Style issues.
    - Code quality suggestions.
    - Potential issues without evidence.
    - Hypothetical problems.
    - Dependency concerns unless a concrete breakage is shown.
    - Missing information as an issue.
    - Documentation changes unless they cause broken behavior.

    OUTPUT RULES:

    If there are no confirmed issues, output EXACTLY:

    No significant issues found.

    Otherwise, use this format for every finding:

    ### [Severity] Short title

    **File:** `path/to/file`

    **Issue:** Describe the confirmed problem.

    **Evidence:** State the specific code or change that proves it.

    **Impact:** Describe the resulting broken behavior or security risk.

    Do not output anything before or after the final review.

    CURRENT PULL REQUEST CHANGES:
    {changes}

    PROJECT CONTEXT:
    {historical_context}
    """

    print(">>> Calling generate_response", flush=True)

    analysis = generate_response(
        prompt
    )

    print(">>> generate_response returned", flush=True)

    print(
        f"Analysis length: {len(analysis or '')}",
        flush=True,
    )

    return analysis.strip()