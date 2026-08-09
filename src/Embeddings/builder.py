import json
OUTPUT_PATH = "data/processed/embedded_documents.json"

def build_embedded_documents(documents, embeddings):
    embedded_documents = []

    for doc, embedding in zip(documents, embeddings):
        embedded_documents.append({
            "id": doc["id"],
            "type": doc["type"],
            "text": doc["text"],
            "embedding": embedding.tolist(),
            "metadata": doc["metadata"]
        })

    return embedded_documents


def save_embedded_documents(embedded_documents):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_documents, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(embedded_documents)} embedded documents to {OUTPUT_PATH}")