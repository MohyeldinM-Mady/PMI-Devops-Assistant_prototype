import json


def process_commits(path="data/commits.json"):
    """
    Reads the raw commits JSON and converts each commit into a
    human-readable text document with metadata, ready for embedding.
    """
    with open(path, "r", encoding="utf-8") as f:
        commits = json.load(f)

    documents = []

    for commit in commits:
        sha_short = commit["sha"][:7]
        author = commit["author"] or "Unknown author"
        date = commit["date"] or "an unknown date"
        message = commit["message"].strip()
        files = commit["files_changed"]

        # Keep the text description readable — summarize file list if long
        if len(files) > 5:
            files_text = ", ".join(files[:5]) + f", and {len(files) - 5} more files"
        elif files:
            files_text = ", ".join(files)
        else:
            files_text = "no files"

        text = (
            f"On {date}, {author} made a commit ({sha_short}): \"{message}\". "
            f"This commit changed: {files_text}."
        )

        document = {
            "id": f"commit_{sha_short}",
            "type": "commit",
            "text": text,
            "metadata": {
                "sha": commit["sha"],
                "author": author,
                "date": date,
                "files_changed": files
            }
        }
        documents.append(document)

    return documents
