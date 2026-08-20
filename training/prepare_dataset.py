import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "training" / "data"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filename):
    path = DATA_DIR / filename

    if not path.exists():
        print(f"Warning: {filename} not found.")
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_example(question, answer, source, metadata=None):
    metadata = metadata or {}

    return {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are PMI, an AI DevOps project knowledge assistant. "
                    "Answer using only the provided project information. "
                    "Do not invent project facts."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
            {
                "role": "assistant",
                "content": answer,
            },
        ],
        "source": source,
        "metadata": metadata,
    }


def process_commits(commits):
    examples = []

    for commit in commits:
        message = commit.get("message", "")
        author = commit.get("author", "unknown")
        date = commit.get("date", "unknown")
        sha = commit.get("sha", "")
        files = commit.get("files_changed", [])

        if not message:
            continue

        files_text = ", ".join(files) if files else "No files recorded."

        examples.append(
            make_example(
                question=f"What happened in commit {sha[:8]}?",
                answer=(
                    f"The commit was '{message}'. "
                    f"It was made by {author} on {date}. "
                    f"The files changed were: {files_text}."
                ),
                source="commit",
                metadata={
                    "sha": sha,
                    "author": author,
                    "date": date,
                },
            )
        )

        examples.append(
            make_example(
                question=f"Which files were affected by the change '{message}'?",
                answer=f"The affected files were: {files_text}.",
                source="commit",
                metadata={
                    "sha": sha,
                },
            )
        )

    return examples


def process_pull_requests(pull_requests):
    examples = []

    for pr in pull_requests:
        number = pr.get("number")
        title = pr.get("title", "")
        body = pr.get("body", "")
        author = pr.get("author", "unknown")
        state = pr.get("state", "unknown")
        merged = pr.get("merged", False)
        created = pr.get("created_at", "unknown")
        merged_at = pr.get("merged_at")
        files = pr.get("files_changed", [])

        files_text = ", ".join(files) if files else "No files recorded."

        status = "merged" if merged else state

        answer = (
            f"Pull request #{number} was titled '{title}'. "
            f"It was created by {author} on {created} and its current state is {status}. "
        )

        if merged_at:
            answer += f"It was merged on {merged_at}. "

        if body:
            answer += f"The PR description states: {body.strip()} "

        answer += f"The files changed were: {files_text}."

        examples.append(
            make_example(
                question=f"What happened in pull request #{number}?",
                answer=answer,
                source="pull_request",
                metadata={
                    "number": number,
                    "author": author,
                    "state": state,
                    "merged": merged,
                },
            )
        )

        examples.append(
            make_example(
                question=f"What files were changed in pull request #{number}?",
                answer=f"The files changed were: {files_text}.",
                source="pull_request",
                metadata={
                    "number": number,
                },
            )
        )

        if body:
            examples.append(
                make_example(
                    question=f"What was the purpose of pull request #{number}?",
                    answer=(
                        f"The purpose of pull request #{number}, '{title}', "
                        f"was described as follows: {body.strip()}"
                    ),
                    source="pull_request",
                    metadata={
                        "number": number,
                    },
                )
            )

    return examples


def process_issues(issues):
    examples = []

    for issue in issues:
        number = issue.get("number", "unknown")
        title = issue.get("title", "")
        body = issue.get("body", "")
        author = issue.get("author", "unknown")
        state = issue.get("state", "unknown")

        examples.append(
            make_example(
                question=f"What is the status of issue #{number}?",
                answer=(
                    f"Issue #{number} is titled '{title}'. "
                    f"It was created by {author} and is currently {state}."
                ),
                source="issue",
                metadata={
                    "number": number,
                    "state": state,
                },
            )
        )

        if body:
            examples.append(
                make_example(
                    question=f"What is issue #{number} about?",
                    answer=body.strip(),
                    source="issue",
                    metadata={
                        "number": number,
                    },
                )
            )

    return examples


def process_docs(docs):
    examples = []

    if not docs:
        return examples

    for i, doc in enumerate(docs):
        if isinstance(doc, str):
            content = doc
            title = f"Document {i + 1}"
        elif isinstance(doc, dict):
            title = (
                doc.get("title")
                or doc.get("name")
                or doc.get("filename")
                or f"Document {i + 1}"
            )

            content = (
                doc.get("content")
                or doc.get("text")
                or doc.get("body")
                or ""
            )
        else:
            continue

        if not content:
            continue

        examples.append(
            make_example(
                question=f"What does the project documentation say about {title}?",
                answer=content.strip(),
                source="documentation",
                metadata={
                    "title": title,
                },
            )
        )

    return examples


def main():
    print("Preparing PMI SFT dataset...")

    commits = load_json("commits.json")
    docs = load_json("docs.json")
    issues = load_json("issues.json")
    pull_requests = load_json("pull_requests.json")

    print(f"Commits: {len(commits)}")
    print(f"Documentation entries: {len(docs)}")
    print(f"Issues: {len(issues)}")
    print(f"Pull requests: {len(pull_requests)}")

    examples = []

    examples.extend(process_commits(commits))
    examples.extend(process_docs(docs))
    examples.extend(process_issues(issues))
    examples.extend(process_pull_requests(pull_requests))

    output_file = OUTPUT_DIR / "sft_dataset.jsonl"

    with open(output_file, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print()
    print(f"Created {len(examples)} SFT examples.")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()