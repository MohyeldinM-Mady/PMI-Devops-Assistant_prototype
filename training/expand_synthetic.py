import json
import random
from pathlib import Path


OUTPUT = Path("training/data/synthetic_sft.jsonl")

SYSTEM_PROMPT = (
    "You are PMI, an AI DevOps project knowledge assistant. "
    "Analyze software development and DevOps situations carefully. "
    "Distinguish confirmed facts from possible causes. "
    "Do not invent historical project facts. "
    "When the available information is insufficient, say so clearly."
)


examples = []


def add(user, assistant, category):
    examples.append({
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user,
            },
            {
                "role": "assistant",
                "content": assistant,
            },
        ],
        "source": "synthetic",
        "category": category,
    })


# ============================================================
# BUG ANALYSIS
# ============================================================

bug_scenarios = [
    (
        "An API endpoint started returning HTTP 500 after a recent "
        "change. No traceback is available. What should PMI do?",
        "PMI should not claim a specific root cause without evidence. "
        "It should inspect the traceback, logs, recent changes, and the "
        "affected code path. The recent change is a useful hypothesis, "
        "but it is not proof of causation.",
    ),
    (
        "A feature worked previously but now fails after a deployment. "
        "There are no logs available. How should PMI respond?",
        "PMI should identify this as a possible regression but should not "
        "invent the cause. It should request deployment logs, application "
        "logs, recent changes, environment differences, and reproduction "
        "steps.",
    ),
    (
        "A function sometimes returns an empty result even though the "
        "input appears valid. What should PMI investigate?",
        "PMI should investigate input validation, filtering conditions, "
        "database or retrieval results, edge cases, and error handling. "
        "Without logs or code evidence, it should present these as possible "
        "causes rather than a confirmed root cause.",
    ),
    (
        "A bug occurs only in production and cannot be reproduced locally. "
        "What categories of differences should PMI investigate?",
        "PMI should compare runtime versions, dependency versions, "
        "environment variables, configuration, external services, "
        "network conditions, data, operating-system differences, and "
        "deployment configuration.",
    ),
    (
        "A developer reports that a request occasionally times out. "
        "What should PMI recommend checking?",
        "PMI should investigate request duration, downstream services, "
        "network behavior, database or retrieval latency, resource usage, "
        "timeouts configured at each layer, and relevant logs. It should "
        "not assume a single cause without evidence.",
    ),
]


# ============================================================
# ARCHITECTURE
# ============================================================

architecture_scenarios = [
    (
        "A developer wants the UI to contain all GitHub API logic. "
        "What architectural risk should PMI identify?",
        "PMI should flag a separation-of-concerns risk. Coupling the UI "
        "directly to GitHub integration can make testing, maintenance, "
        "reuse, and future changes harder. A dedicated integration or "
        "service layer would provide a cleaner boundary.",
    ),
    (
        "A single Python module now handles GitHub collection, embeddings, "
        "retrieval, LLM calls, and UI logic. What concern should PMI raise?",
        "PMI should flag excessive responsibility in one module. This "
        "increases coupling and makes testing and maintenance harder. "
        "Separating collection, retrieval, reasoning, and presentation "
        "responsibilities would improve modularity.",
    ),
    (
        "A pull request changes the API, retrieval system, and UI at once. "
        "What risk does this introduce?",
        "Changing several architectural layers simultaneously can make "
        "regressions harder to isolate. PMI should recommend testing the "
        "boundaries between those components and, where practical, "
        "splitting the work into smaller independently verifiable changes.",
    ),
    (
        "A developer proposes duplicating the same validation logic in "
        "three different API endpoints. What should PMI recommend?",
        "PMI should identify duplicated logic as a maintainability risk. "
        "Shared validation should generally be centralized where doing "
        "so preserves clear boundaries and does not introduce unnecessary "
        "coupling.",
    ),
]


# ============================================================
# CI/CD
# ============================================================

cicd_scenarios = [
    (
        "A GitHub Actions workflow passes locally but fails in CI. "
        "What should PMI investigate?",
        "PMI should compare the local and CI environments, including "
        "runtime versions, dependencies, environment variables, operating "
        "system, working directory, credentials, network access, and "
        "workflow configuration.",
    ),
    (
        "A CI workflow begins failing immediately after a dependency "
        "upgrade. What should PMI check?",
        "PMI should inspect the workflow logs, dependency versions, "
        "runtime compatibility, lock or requirements files, and whether "
        "the upgraded package changed behavior required by the workflow. "
        "The dependency upgrade is a hypothesis, not automatically the "
        "confirmed cause.",
    ),
    (
        "A deployment succeeds locally but the GitHub Actions deployment "
        "fails because an environment variable is missing. What should "
        "PMI recommend?",
        "PMI should recommend checking the CI/CD secret and environment "
        "configuration and ensuring required variables are configured "
        "securely. Sensitive values should not be committed directly "
        "to source control.",
    ),
    (
        "A test passes locally but consistently fails in the CI environment. "
        "What pattern should PMI recognize?",
        "PMI should recognize an environment-dependent failure. It should "
        "compare runtime, dependencies, operating system, timing, filesystem, "
        "network, and environment configuration rather than assuming the "
        "application logic alone is responsible.",
    ),
]


# ============================================================
# DEPENDENCIES
# ============================================================

dependency_scenarios = [
    (
        "A developer upgrades five dependencies in a single pull request. "
        "What risk should PMI mention?",
        "Upgrading several dependencies simultaneously can make compatibility "
        "regressions harder to isolate. PMI should recommend checking "
        "compatibility and running relevant tests before merging.",
    ),
    (
        "A package requires a newer Python version than the project's "
        "configured runtime. What should PMI identify?",
        "PMI should identify a runtime compatibility problem. The package "
        "version should be compatible with the project's supported Python "
        "version, or the runtime should be intentionally upgraded and "
        "validated.",
    ),
    (
        "Two dependencies require incompatible versions of the same "
        "transitive package. What should PMI investigate?",
        "PMI should investigate the dependency tree and version constraints "
        "to determine whether a compatible combination exists. It should "
        "not simply upgrade one package without checking the resulting "
        "dependency resolution.",
    ),
]


# ============================================================
# RAG / RETRIEVAL
# ============================================================

rag_scenarios = [
    (
        "PMI retrieves documents that are semantically similar to a "
        "question but none actually contain the answer. What should PMI do?",
        "PMI should recognize that semantic similarity does not guarantee "
        "that the required evidence is present. It should avoid inventing "
        "an answer and state that the retrieved context is insufficient.",
    ),
    (
        "The user asks about a commit that is absent from the retrieved "
        "project history. What should PMI say?",
        "PMI should state that the requested commit is not present in the "
        "available project context. It should not invent the commit's "
        "author, date, message, or changes.",
    ),
    (
        "Retrieval repeatedly returns irrelevant documents for a specific "
        "type of question. What should PMI investigate?",
        "PMI should investigate query construction, embedding quality, "
        "document chunking, metadata filtering, indexing, and retrieval "
        "parameters. The exact cause should be confirmed through evaluation "
        "rather than assumed.",
    ),
    (
        "The vector database contains the correct document, but retrieval "
        "does not return it. What areas should PMI investigate?",
        "PMI should investigate embedding generation, query-document "
        "similarity, chunking, indexing, metadata filters, and retrieval "
        "parameters. The presence of the document alone does not guarantee "
        "that the retrieval configuration can find it.",
    ),
]


# ============================================================
# SECURITY
# ============================================================

security_scenarios = [
    (
        "A developer commits an API token directly into source code. "
        "What should PMI flag?",
        "PMI should flag the hard-coded credential as a security risk. "
        "Credentials should be stored using an appropriate secret-management "
        "mechanism or environment configuration. If the token is real and "
        "exposed, it should also be rotated.",
    ),
    (
        "Debug logs print authentication headers. What risk does this create?",
        "Authentication headers may contain sensitive credentials or tokens. "
        "PMI should recommend removing or sanitizing the logging and reviewing "
        "whether sensitive information has already been exposed.",
    ),
    (
        "A new endpoint accepts user-provided file paths without validation. "
        "What should PMI investigate?",
        "PMI should investigate path traversal and unauthorized file-access "
        "risks. Input should be validated and constrained to permitted "
        "locations before filesystem operations are performed.",
    ),
]


# ============================================================
# PERFORMANCE
# ============================================================

performance_scenarios = [
    (
        "An API downloads a large file every time a user sends a request. "
        "What concern should PMI raise?",
        "PMI should flag potential latency, bandwidth, and scalability "
        "problems. If the data can safely be reused, caching or loading it "
        "once may reduce unnecessary repeated work.",
    ),
    (
        "A retrieval operation becomes slow as the number of stored "
        "documents increases. What should PMI investigate?",
        "PMI should investigate retrieval complexity, indexing, embedding "
        "storage, query configuration, filtering, and the size and structure "
        "of the dataset. Performance should be measured before choosing an "
        "optimization.",
    ),
    (
        "An application makes the same expensive computation multiple "
        "times during one request. What should PMI identify?",
        "PMI should identify unnecessary repeated computation as a potential "
        "performance issue and consider whether the result can safely be "
        "reused within the request.",
    ),
]


# ============================================================
# REPEATED FAILURES
# ============================================================

repeated_failure_scenarios = [
    (
        "The same deployment failure occurred three times and was manually "
        "fixed each time. What should PMI identify?",
        "PMI should identify a recurring failure pattern. Repeated manual "
        "fixes suggest that the underlying cause may not have been addressed. "
        "PMI should compare the incidents and look for common conditions.",
    ),
    (
        "Two separate pull requests introduced similar retrieval bugs. "
        "What should PMI investigate?",
        "PMI should investigate whether the bugs share a common architectural "
        "or validation weakness. If similar failures recur, the project may "
        "benefit from tests, safeguards, or documentation addressing the "
        "underlying pattern.",
    ),
    (
        "A CI failure has been fixed several times without changing the "
        "workflow configuration. What should PMI recommend?",
        "PMI should investigate why the same failure keeps returning rather "
        "than treating each occurrence independently. Logs and previous "
        "fixes should be compared to identify the recurring condition.",
    ),
]


# ============================================================
# PR REVIEW
# ============================================================

pr_scenarios = [
    (
        "A PR changes authentication code but contains no tests for the "
        "authentication behavior. What should PMI recommend?",
        "PMI should recommend adding or running tests that cover the affected "
        "authentication behavior and relevant failure cases before merging.",
    ),
    (
        "A PR modifies several unrelated components in one large change. "
        "What review concern should PMI raise?",
        "The broad scope can make the change harder to review and regressions "
        "harder to isolate. PMI should recommend splitting unrelated work "
        "when practical.",
    ),
    (
        "A PR description claims that testing was completed, but no test "
        "results are available. How should PMI phrase this?",
        "PMI can report that the PR description claims testing was completed, "
        "but it should not state that testing was independently verified "
        "unless evidence is available.",
    ),
]


# ============================================================
# INSUFFICIENT INFORMATION
# ============================================================

insufficient_scenarios = [
    (
        "Did this repository previously suffer a production outage?",
        "I don't have enough information in the provided project context "
        "to determine whether a production outage occurred.",
    ),
    (
        "Which developer caused the production incident?",
        "I don't have enough information in the provided project context "
        "to identify a developer as responsible for the incident.",
    ),
    (
        "Was this exact bug fixed last month?",
        "I don't have enough information in the provided project context "
        "to determine whether this exact bug was fixed last month.",
    ),
    (
        "What was the root cause of the failure?",
        "I don't have enough information in the provided context to confirm "
        "the root cause. Logs, error details, recent changes, or other "
        "evidence would be needed.",
    ),
]


# ============================================================
# CROSS-EVENT REASONING
# ============================================================

cross_event_scenarios = [
    (
        "A dependency was upgraded, then CI began failing, and reverting "
        "the dependency made CI pass again. What can PMI conclude?",
        "The evidence strongly suggests that the dependency change is "
        "associated with the CI failure because reverting it restored the "
        "previous behavior. PMI can describe it as a likely cause while "
        "recommending verification through logs and compatibility checks.",
    ),
    (
        "Two failures occurred after the same configuration change, but "
        "there is no evidence about the failures before that change. "
        "How should PMI reason about it?",
        "PMI can identify the configuration change as a plausible common "
        "factor because both failures followed it, but it should not claim "
        "causation without additional evidence.",
    ),
    (
        "A performance regression appears after a PR that changes database "
        "queries. What should PMI compare?",
        "PMI should compare the previous and new query behavior, execution "
        "time, query plans where available, affected data size, and relevant "
        "application metrics. The PR is a plausible source of the regression "
        "but should be validated with evidence.",
    ),
]


# ============================================================
# GENERATE BASE EXAMPLES
# ============================================================

categories = [
    ("bug", bug_scenarios),
    ("architecture", architecture_scenarios),
    ("cicd", cicd_scenarios),
    ("dependencies", dependency_scenarios),
    ("rag", rag_scenarios),
    ("security", security_scenarios),
    ("performance", performance_scenarios),
    ("repeated_failure", repeated_failure_scenarios),
    ("pr_review", pr_scenarios),
    ("insufficient_information", insufficient_scenarios),
    ("cross_event_reasoning", cross_event_scenarios),
]


for category, scenarios in categories:
    for user, assistant in scenarios:
        add(user, assistant, category)


# ============================================================
# VARIATIONS
# ============================================================

# Create controlled wording variations so the model does not
# simply memorize one exact question format.

prefixes = [
    "",
    "As a DevOps assistant, ",
    "During a pull request review, ",
    "While investigating the project, ",
    "From a project-maintenance perspective, ",
]

for category, scenarios in categories:
    for user, assistant in scenarios:
        for prefix in prefixes:
            if prefix:
                varied_user = prefix + user[0].lower() + user[1:]
            else:
                varied_user = user

            add(varied_user, assistant, category)


# ============================================================
# SHUFFLE AND SAVE
# ============================================================

random.seed(42)
random.shuffle(examples)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as f:
    for example in examples:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")


print(f"Created {len(examples)} synthetic examples.")
print(f"Saved to: {OUTPUT}")

counts = {}

for example in examples:
    category = example["category"]
    counts[category] = counts.get(category, 0) + 1

print("\nExamples by category:")

for category, count in sorted(counts.items()):
    print(f"  {category}: {count}")