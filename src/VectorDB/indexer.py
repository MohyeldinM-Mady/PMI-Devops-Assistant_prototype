import json

from src.VectorDB.database import reset_collection
from src.VectorDB.loader import load_embedded_documents


def _clean_metadata(metadata):
    clean = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        clean[key] = value
    return clean


def index_documents(reset: bool = True):
    documents = load_embedded_documents()
    collection = reset_collection() if reset else __import__("src.VectorDB.database", fromlist=["get_collection"]).get_collection()

    for doc in documents:
        metadata = {
            **doc.get("metadata", {}),
            "type": doc["type"],
        }
        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            embeddings=[doc["embedding"]],
            metadatas=[_clean_metadata(metadata)],
        )

    print(f"Indexed {len(documents)} documents")
    return collection
