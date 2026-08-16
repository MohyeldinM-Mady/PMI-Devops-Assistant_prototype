import json

from src.config import DATA_DIR


def process_issues(path=DATA_DIR / "issues.json"):
    with open(path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    documents = []
    for issue in issues:
        number = issue["number"]
        title = issue.get("title") or "Untitled issue"
        author = issue.get("author") or "unknown author"
        state = issue.get("state") or "unknown"
        created_at = issue.get("created_at") or "unknown date"
        labels = issue.get("labels") or []
        comments = issue.get("comments", 0)
        labels_text = f" Labels: {', '.join(labels)}." if labels else ""

        documents.append({
            "id": f"issue_{number}",
            "type": "issue",
            "text": f'Issue #{number} "{title}" was opened by {author} on {created_at} and is currently {state}.{labels_text} It has {comments} comment(s).',
            "metadata": {
                "number": number,
                "title": title,
                "author": author,
                "state": state,
                "date": created_at,
                "labels": labels,
            },
        })
    return documents
