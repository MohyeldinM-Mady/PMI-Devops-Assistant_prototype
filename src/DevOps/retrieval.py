from src.Retrieval.query import retrieve_documents
from src.Retrieval.context import build_context


def retrieve_historical_context(files: list[dict], n_results=3) -> str:
    query_parts = []

    for file in files:
        query_parts.append(
            f"File: {file['filename']}\n"
            f"Status: {file['status']}\n"
            f"Changes:\n{file['patch']}"
        )

    query = "\n\n".join(query_parts)

    results = retrieve_documents(
        query,
        n_results=n_results,
    )

    return build_context(results)