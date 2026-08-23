from src.Retrieval.embedder import embed_query
from src.VectorDB.database import get_collection


def similarity_search(query_text: str, n_results: int = 3, where=None):
    collection = get_collection()
    return collection.query(
        query_embeddings=[embed_query(query_text)],
        n_results=n_results,
        where=where,
    )
