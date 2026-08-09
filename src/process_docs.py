import json


def process_docs(path="data/docs.json"):
    """
    Reads the raw docs JSON and converts each markdown document into a
    human-readable text document with metadata, ready for embedding.
    """
    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    documents = []

    for doc in docs:
        filename = doc["filename"]
        doc_path = doc["path"]
        content = doc["content"].strip()

        # Truncate very long docs for the text summary, keep full content in metadata
        if len(content) > 1000:
            content_preview = content[:1000] + "... [truncated]"
        else:
            content_preview = content

        text = (
            f"Documentation file \"{filename}\" (located at {doc_path}) contains the following content:\n"
            f"{content_preview}"
        )

        document = {
            "id": f"doc_{filename.replace('.', '_')}",
            "type": "doc",
            "text": text,
            "metadata": {
                "filename": filename,
                "path": doc_path,
                "full_content": content
            }
        }
        documents.append(document)

    return documents
