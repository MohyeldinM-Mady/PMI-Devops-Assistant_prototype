import json

from src.config import PROCESSED_DIR

OUTPUT_PATH = PROCESSED_DIR / "embedded_documents.json"


def build_embedded_documents(documents, embeddings):
    if len(documents) != len(embeddings):
        raise ValueError("Document count and embedding count do not match.")

    return [
        {
            "id": doc["id"],
            "type": doc["type"],
            "text": doc["text"],
            "embedding": embedding.tolist(),
            "metadata": doc["metadata"],
        }
        for doc, embedding in zip(documents, embeddings)
    ]


def save_embedded_documents(embedded_documents):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_documents, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(embedded_documents)} embedded documents to {OUTPUT_PATH}")
