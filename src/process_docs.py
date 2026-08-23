import json

from src.config import DATA_DIR


def process_docs(path=DATA_DIR / "docs.json"):
    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    documents = []

    for doc in docs:
        filename = doc["filename"]
        doc_path = doc["path"]
        content = (doc.get("content") or "").strip()

        normalized_filename = filename.strip().lower()

        text = (
            f'Documentation file "{filename}" (located at {doc_path}) contains the following content:\n'
            f"{content}"
        )

        documents.append({
            "id": f"doc_{normalized_filename.replace('.', '_')}",
            "type": "doc",
            "text": text,
            "metadata": {
                "filename": filename,
                "path": doc_path,
                "full_content": content,
            },
        })

    return documents