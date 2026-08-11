from src.VectorDB.loader import load_embedded_documents
from src.VectorDB.database import get_collection


def index_documents():
    documents = load_embedded_documents()
    collection = get_collection()

    for doc in documents:
        metadata = {
            **doc["metadata"],
            "type": doc["type"],
        }

        clean_metadata = {}

        for key, value in metadata.items():
            if value is None:
                continue

            if isinstance(value, list):
                if not value:
                    continue

                value = ", ".join(str(item) for item in value)

            clean_metadata[key] = value

        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            embeddings=[doc["embedding"]],
            metadatas=[clean_metadata],
        )

    print(f"Indexed {len(documents)} documents")