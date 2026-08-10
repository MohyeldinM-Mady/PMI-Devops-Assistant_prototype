from src.VectorDB.loader import load_embedded_documents
from src.VectorDB.database import get_collection


def index_documents():
    documents = load_embedded_documents()
    collection = get_collection()

    for doc in documents:
        metadata = {
          **doc["metadata"],
          "type": doc["type"]
       }
        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            embeddings=[doc["embedding"]],
            metadatas=[metadata],
        )

    print(f"Indexed {len(documents)} documents")