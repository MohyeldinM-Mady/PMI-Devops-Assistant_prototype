import chromadb

from src.config import CHROMA_DIR

COLLECTION_NAME = "pmi_knowledge_chroma"


def get_client():
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    return get_client().get_or_create_collection(name=COLLECTION_NAME)


def reset_collection():
    client = get_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    return client.get_or_create_collection(name=COLLECTION_NAME)
