from src.Embeddings.loader import load_documents
from src.Embeddings.generator import generate_embeddings
from src.Embeddings.builder import build_embedded_documents, save_embedded_documents

def main():

    documents = load_documents()
    print(f"Loaded {len(documents)} documents")

    embeddings = generate_embeddings(documents)
    print(f"Generated embeddings: {embeddings.shape}")

    embedded_documents = build_embedded_documents(
        documents,
        embeddings
    )
    print(f"Built {len(embedded_documents)} embedded documents")

    save_embedded_documents(embedded_documents)
    
if __name__ == "__main__":
    main()