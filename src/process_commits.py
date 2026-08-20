import json

from src.config import DATA_DIR


def process_commits(path=DATA_DIR / "commits.json"):
    with open(path, "r", encoding="utf-8") as f:
        commits = json.load(f)

    documents = []
    for commit in commits:
        sha = commit["sha"]
        message = (commit.get("message") or "").strip()
        files = commit.get("files_changed") or []
        author = commit.get("author") or "Unknown author"
        date = commit.get("date") or "unknown date"
        files_text = ", ".join(files[:5]) + (f", and {len(files) - 5} more files" if len(files) > 5 else "") if files else "no files"

        documents.append({
            "id": f"commit_{sha[:7]}",
            "type": "commit",
            "text": f'On {date}, {author} made a commit ({sha[:7]}): "{message}". This commit changed: {files_text}.',
            "metadata": {
                "sha": sha,
                "author": author,
                "date": date,
                "message": message,
                "files_changed": files,
            },
        })
    return documents
