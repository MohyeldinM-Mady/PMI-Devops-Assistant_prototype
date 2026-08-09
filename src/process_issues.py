import json


def process_issues(path="data/issues.json"):
    """
    Reads the raw issues JSON and converts each issue into a
    human-readable text document with metadata, ready for embedding.
    """
    with open(path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    documents = []

    for issue in issues:
        number = issue["number"]
        title = issue["title"]
        author = issue["author"] or "an unknown author"
        state = issue["state"]
        created_at = issue["created_at"] or "an unknown date"
        labels = issue["labels"]
        comments = issue["comments"]

        labels_text = f" Labels: {', '.join(labels)}." if labels else ""

        text = (
            f"Issue #{number} \"{title}\" was opened by {author} on {created_at} "
            f"and is currently {state}.{labels_text} It has {comments} comment(s)."
        )

        document = {
            "id": f"issue_{number}",
            "type": "issue",
            "text": text,
            "metadata": {
                "number": number,
                "author": author,
                "state": state,
                "created_at": created_at,
                "labels": labels
            }
        }
        documents.append(document)

    return documents
