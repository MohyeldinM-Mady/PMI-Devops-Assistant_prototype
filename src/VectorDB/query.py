from src.VectorDB.database import get_collection


def similarity_search(query_text, n_results=3, where=None):
    collection = get_collection()

    return collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where,
    )