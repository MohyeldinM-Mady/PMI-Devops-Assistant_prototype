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

    Your goal is to identify real, actionable problems introduced by the pull request.
    You must prioritize accuracy over the number of findings.

    Use ONLY:
    1. The current pull request diff.
    2. The supplied historical project context.

    Do not invent facts, code, files, functions, endpoints, dependencies, or behavior.

    IMPORTANT REVIEW RULES:

    1. Only report an issue when it is directly supported by the provided code or PR diff.

    2. Do NOT assume that something is missing simply because it is not visible in the diff.
    A Git diff may contain only changed portions of a file.
    Unchanged code may exist outside the displayed diff.

    3. NEVER claim that an endpoint, function, import, file, dependency, configuration,
    or module is missing unless the provided repository context actually proves that it
    is missing.

    4. Do NOT interpret an incomplete or truncated diff as evidence that the source file
    itself is incomplete or syntactically invalid.

    5. Do NOT report hypothetical or speculative problems as confirmed findings.

    6. Distinguish between:
    - Confirmed Bug: A concrete defect that can be demonstrated from the available code.
    - Potential Risk: A plausible concern that cannot be fully confirmed.
    - Suggestion: A possible improvement that is not a bug.

    7. Only report CONFIRMED BUGS under the "Findings" section.
    Do not turn general code-quality suggestions into bugs.

    8. Every finding MUST contain concrete evidence:
    - File path
    - Relevant function, class, or code section
    - Clear explanation of why the code causes the problem

    9. Before reporting a finding, verify that the evidence actually exists in the supplied
    PR diff or historical context.

    10. If you cannot verify a suspected issue, DO NOT report it.

    11. Prefer reporting "No significant issues found" over making an unsupported claim.

    12. Do not report trivial formatting issues, such as missing trailing newlines,
    unless they directly affect functionality.

    13. Do not report intentional limits, constants, or design decisions as bugs unless
    the provided context demonstrates that they cause an actual problem.

    14. Do not expose your internal reasoning or chain-of-thought.
    Return only the final review.

    15. Keep the review concise and focused on actionable findings.

    CURRENT PULL REQUEST:
    {changes}

    HISTORICAL PROJECT CONTEXT:
    {historical_context or "No relevant historical context was found."}

    Return the final review using exactly this structure:

    ## Summary
    Briefly describe what the pull request changes.

    ## Findings
    List only confirmed bugs that are directly supported by the available evidence.

    For each finding use:

    ### [Severity] Finding title
    **File:** `path/to/file.py`

    **Evidence:** Describe the relevant code or function.

    **Impact:** Explain the concrete effect of the problem.

    If no confirmed bugs are found, write:
    "No significant issues found."

    ## Recommendations
    Provide concise, actionable recommendations only when they are justified by
    the confirmed findings.

    If there are no confirmed bugs, write:
    "No changes required based on the available evidence."
    """

    analysis = generate_response(
        prompt,
        max_tokens=4096,
        temperature=0.1,
    )

    print(f"Analysis length: {len(analysis or '')}")

    return analysis.strip()