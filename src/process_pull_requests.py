import json


def process_pull_requests(path="data/pull_requests.json"):
    """
    Reads the raw pull requests JSON and converts each PR into a
    human-readable text document with metadata, ready for embedding.
    """
    with open(path, "r", encoding="utf-8") as f:
        prs = json.load(f)

    documents = []

    for pr in prs:
        number = pr["number"]
        title = pr["title"]
        author = pr["author"] or "an unknown author"
        state = pr["state"]
        merged = pr["merged"]
        created_at = pr["created_at"] or "an unknown date"
        files = pr["files_changed"]
        linked_issues = pr["linked_issues"]

        status_text = "merged" if merged else state

        if len(files) > 5:
            files_text = ", ".join(files[:5]) + f", and {len(files) - 5} more files"
        elif files:
            files_text = ", ".join(files)
        else:
            files_text = "no files"

        linked_text = (
            f" It references issue(s): {', '.join(linked_issues)}."
            if linked_issues else ""
        )

        text = (
            f"Pull request #{number} \"{title}\" was opened by {author} on {created_at} "
            f"and is currently {status_text}. It changed: {files_text}.{linked_text}"
        )

        document = {
            "id": f"pr_{number}",
            "type": "pull_request",
            "text": text,
            "metadata": {
                "number": number,
                "author": author,
                "state": state,
                "merged": merged,
                "created_at": created_at,
                "files_changed": files,
                "linked_issues": linked_issues
            }
        }
        documents.append(document)

    return documents
