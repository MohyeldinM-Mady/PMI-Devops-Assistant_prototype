from src.VectorDB.database import get_collection
from src.VectorDB.indexer import index_documents


def main():
    collection = index_documents(reset=True)
    print(f"Total documents in ChromaDB: {collection.count()}")


if __name__ == "__main__":
    main()
