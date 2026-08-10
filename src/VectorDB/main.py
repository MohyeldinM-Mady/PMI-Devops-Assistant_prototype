from src.VectorDB.indexer import index_documents
from src.VectorDB.database import get_collection


def main():
    index_documents()

    collection = get_collection()
    print(f"Total documents in ChromaDB: {collection.count()}")


if __name__ == "__main__":
    main()