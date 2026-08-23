from src.Retrieval.main import retrieve_context

MAX_PATCH_PER_FILE = 6000
MAX_QUERY_LENGTH = 30000


def retrieve_historical_context(files: list[dict], n_results=5) -> str:
    query_parts = []
    for file in files:
        patch = (file.get("patch") or "")[:MAX_PATCH_PER_FILE]
        query_parts.append(
            f"File: {file.get('filename', 'unknown')}\n"
            f"Status: {file.get('status', 'unknown')}\n"
            f"Changes:\n{patch}"
        )

    query = "\n\n".join(query_parts)[:MAX_QUERY_LENGTH]
    return retrieve_context(query, n_results=n_results)
