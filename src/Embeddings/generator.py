from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings(documents):
    texts = [doc["text"] for doc in documents]

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )

    return embeddings
