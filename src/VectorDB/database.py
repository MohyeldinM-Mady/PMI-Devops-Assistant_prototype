import chromadb


def get_collection():
    client = chromadb.PersistentClient(path="data/chroma")

    collection = client.get_or_create_collection(
        name="pmi_knowledge_chroma"
    )

    return collection
