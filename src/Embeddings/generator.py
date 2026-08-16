from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(documents):
    texts = [doc["text"] for doc in documents]
    return get_model().encode(texts, show_progress_bar=True, convert_to_numpy=True)
