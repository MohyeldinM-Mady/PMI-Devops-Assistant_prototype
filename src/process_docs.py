import json

from src.config import DATA_DIR


def process_docs(path=DATA_DIR / "docs.json"):
    """Process documentation without truncating the text used for embeddings.

    The full document is kept in the searchable text so semantic retrieval can
    answer architecture/project-level questions that occur later in README.md.
    ``full_content`` remains in metadata for exact document retrieval.
    """
    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    documents = []
    for doc in docs:
        filename = doc["filename"]
        doc_path = doc["path"]
        content = (doc.get("content") or "").strip()

        text = (
            f'Documentation file "{filename}" (located at {doc_path}) contains the following content:\n'
            f"{content}"
        )

        documents.append({
            "id": f"doc_{filename.replace('.', '_')}",
            "type": "doc",
            "text": text,
            "metadata": {
                "filename": filename,
                "path": doc_path,
                "full_content": content,
            },
        })
    return documents
