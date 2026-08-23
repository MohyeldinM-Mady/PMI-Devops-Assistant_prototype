import json

from src.config import DATA_DIR


def process_pull_requests(path=DATA_DIR / "pull_requests.json"):
    with open(path, "r", encoding="utf-8") as f:
        prs = json.load(f)

    documents = []
    for pr in prs:
        number = pr["number"]
        title = pr.get("title") or "Untitled pull request"
        author = pr.get("author") or "unknown author"
        state = pr.get("state") or "unknown"
        merged = bool(pr.get("merged"))
        created_at = pr.get("created_at") or "unknown date"
        files = pr.get("files_changed") or []
        linked_issues = pr.get("linked_issues") or []
        status = "merged" if merged else state
        files_text = ", ".join(files[:5]) + (f", and {len(files) - 5} more files" if len(files) > 5 else "") if files else "no files"
        linked_text = f" It references issue(s): {', '.join(linked_issues)}." if linked_issues else ""

        documents.append({
            "id": f"pr_{number}",
            "type": "pull_request",
            "text": f'Pull request #{number} "{title}" was opened by {author} on {created_at} and is currently {status}. It changed: {files_text}.{linked_text}',
            "metadata": {
                "number": number,
                "title": title,
                "author": author,
                "state": state,
                "merged": merged,
                "date": created_at,
                "files_changed": files,
                "linked_issues": linked_issues,
            },
        })
    return documents
