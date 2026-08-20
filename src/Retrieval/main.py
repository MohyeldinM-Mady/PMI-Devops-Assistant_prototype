from src.Retrieval.context import build_context
from src.Retrieval.query import retrieve_documents


def retrieve_context(query: str, n_results: int = 3) -> str:
    results = retrieve_documents(query, n_results=n_results)
    return build_context(results)


def main():
    query = input("Ask a question: ").strip()
    print("\nRetrieved Context:\n")
    print(retrieve_context(query))


if __name__ == "__main__":
    main()
