from datetime import datetime, timezone



ORDER_FIELDS = {
    "commit": "date",
    "pull_request": "date",
    "issue": "date",
}

ENTITY_ID_PREFIX = {
    "commit": "commit",
    "pull_request": "pr",
    "issue": "issue",
    "doc": "doc",
}


def canonical_document_id(entity: str, identifier: str) -> str | None:
    if identifier is None:
        return None
    identifier = str(identifier)
    prefix = ENTITY_ID_PREFIX.get(entity)
    if not prefix:
        return None
    if entity == "doc":
        return f"doc_{identifier.replace('.', '_')}"
    if entity == "commit":
        return f"commit_{identifier[:7]}"
    return f"{prefix}_{identifier}"


def _tokenize(text: str) -> set[str]:
    import re

    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "by", "do", "does",
        "for", "from", "how", "in", "is", "it", "of", "on", "or", "the",
        "this", "to", "what", "where", "which", "who", "with", "project",
    }
    return {
        token for token in re.findall(r"[a-z0-9_]+", text.lower())
        if token not in stop_words and len(token) > 1
    }


def _lexical_score(query: str, document: str) -> float:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0.0

    document_tokens = _tokenize(document)
    overlap = query_tokens & document_tokens
    if not overlap:
        return 0.0

    coverage = len(overlap) / len(query_tokens)
    density = len(overlap) / max(len(document_tokens), 1)
    return coverage + min(density * 10.0, 0.25)


def _project_level_query(query: str) -> bool:
    lowered = query.lower()
    markers = (
        "purpose", "what does the project", "what is the project", "what is pmi", "what problem does pmi",
        "how does the project", "project architecture", "architecture",
        "knowledge base", "project memory", "retrieval", "rag",
        "embedding", "vector database", "phases",
    )
    return any(marker in lowered for marker in markers)


def retrieve_documents(query: str, n_results: int = 3):
    """Hybrid retrieval: vector recall + lexical/project-document reranking.

    Vector search remains the primary semantic signal. A lightweight lexical
    signal is added because project documentation is highly structured and
    exact terms such as ``retrieval`` or ``knowledge base`` are valuable.
    Project-level questions also receive a small documentation boost so a
    README is not buried beneath individual commits.
    """
    if not query.strip():
        return _build_result([])

    from src.Retrieval.embedder import embed_query
    from src.VectorDB.database import get_collection

    collection = get_collection()
    candidate_k = max(n_results * 4, 20)
    vector_results = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=candidate_k,
    )

    vector_ids = vector_results.get("ids", [[]])[0]
    vector_documents = vector_results.get("documents", [[]])[0]
    vector_metadatas = vector_results.get("metadatas", [[]])[0]
    vector_distances = vector_results.get("distances", [[]])[0]

    vector_records = []
    for index, (doc_id, document, metadata) in enumerate(
        zip(vector_ids, vector_documents, vector_metadatas)
    ):
        distance = vector_distances[index] if index < len(vector_distances) else 1.0
        vector_score = 1.0 / (1.0 + float(distance))
        searchable = document or ""
        if metadata.get("type") == "doc":
            searchable += "\n" + str(metadata.get("full_content", ""))
        lexical = _lexical_score(query, searchable)
        project_boost = 0.20 if _project_level_query(query) and metadata.get("type") == "doc" else 0.0
        score = vector_score + (0.65 * lexical) + project_boost
        vector_records.append((score, doc_id, document, metadata))

    # Add a small lexical recall pass over the whole collection. This catches
    # important terms that may not be represented in a truncated/older index.
    all_results = collection.get()
    lexical_records = []
    for doc_id, document, metadata in zip(
        all_results.get("ids", []),
        all_results.get("documents", []),
        all_results.get("metadatas", []),
    ):
        searchable = document or ""
        if metadata.get("type") == "doc":
            searchable += "\n" + str(metadata.get("full_content", ""))
        lexical = _lexical_score(query, searchable)
        project_boost = 0.20 if _project_level_query(query) and metadata.get("type") == "doc" else 0.0
        if lexical > 0.0 or project_boost:
            lexical_records.append((0.65 * lexical + project_boost, doc_id, document, metadata))

    merged = {}
    for score, doc_id, document, metadata in vector_records + lexical_records:
        existing = merged.get(doc_id)
        if existing is None or score > existing[0]:
            merged[doc_id] = (score, doc_id, document, metadata)

    ranked = sorted(merged.values(), key=lambda item: item[0], reverse=True)[:n_results]
    return {
        "ids": [[item[1] for item in ranked]],
        "documents": [[item[2] for item in ranked]],
        "metadatas": [[item[3] for item in ranked]],
    }


def retrieve_by_id(document_id: str):
    from src.VectorDB.database import get_collection
    collection = get_collection()
    results = collection.get(ids=[document_id])
    return {
        "ids": [results.get("ids", [])],
        "documents": [results.get("documents", [])],
        "metadatas": [results.get("metadatas", [])],
    }


def retrieve_by_type(document_type: str):
    from src.VectorDB.database import get_collection
    collection = get_collection()
    results = collection.get(where={"type": document_type})
    return {
        "ids": [results.get("ids", [])],
        "documents": [results.get("documents", [])],
        "metadatas": [results.get("metadatas", [])],
    }


def retrieve_all_changed_files():
    """Return the unique union of files changed by commits and PRs."""
    from src.VectorDB.database import get_collection
    collection = get_collection()
    files: set[str] = set()

    for entity in ("commit", "pull_request"):
        results = collection.get(where={"type": entity})
        for metadata in results.get("metadatas", []) or []:
            raw = metadata.get("files_changed", [])
            if isinstance(raw, str):
                import json
                try:
                    raw = json.loads(raw)
                except json.JSONDecodeError:
                    raw = [item.strip() for item in raw.split(",") if item.strip()]
            files.update(str(item) for item in (raw or []) if str(item).strip())

    return sorted(files, key=str.casefold)


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (ValueError, TypeError):
        return None


def _get_identifier(metadata, entity):
    if entity == "commit":
        return metadata.get("sha")
    if entity in {"pull_request", "issue"}:
        value = metadata.get("number")
        return str(value) if value is not None else None
    if entity == "doc":
        return metadata.get("filename")
    return None


def _identifier_matches(metadata, entity, identifier):
    actual = _get_identifier(metadata, entity)
    if actual is None or identifier is None:
        return False
    actual = str(actual)
    identifier = str(identifier).strip()
    return actual.startswith(identifier) if entity == "commit" else actual == identifier


def _sort_records(records, entity):
    order_field = ORDER_FIELDS.get(entity)
    if not order_field:
        return records

    def key(record):
        parsed = _parse_date(record[2].get(order_field))
        return (parsed is None, parsed or datetime.max.replace(tzinfo=timezone.utc))

    return sorted(records, key=key)


def _build_result(records):
    return {
        "ids": [[record[0] for record in records]],
        "documents": [[record[1] for record in records]],
        "metadatas": [[record[2] for record in records]],
    }


def retrieve_relative(entity: str, identifier: str, relation: str):
    if relation not in {"previous", "next"} or entity not in ORDER_FIELDS or identifier is None:
        return _build_result([])

    from src.VectorDB.database import get_collection
    collection = get_collection()
    results = collection.get(where={"type": entity})
    records = list(zip(
        results.get("ids", []),
        results.get("documents", []),
        results.get("metadatas", []),
    ))
    records = _sort_records(records, entity)

    reference_index = next(
        (index for index, record in enumerate(records)
         if _identifier_matches(record[2], entity, identifier)),
        None,
    )
    if reference_index is None:
        return _build_result([])

    target_index = reference_index - 1 if relation == "previous" else reference_index + 1
    if not 0 <= target_index < len(records):
        return _build_result([])

    return _build_result([records[target_index]])


def retrieve(entity: str, operation: str, identifier: str | None = None,
             query: str | None = None, n_results: int = 5):
    if operation == "get":
        document_id = canonical_document_id(entity, identifier) if identifier else None
        return retrieve_by_id(document_id) if document_id else _build_result([])

    if operation == "list":
        return retrieve_by_type(entity)

    if operation == "search":
        return retrieve_documents(query or "", n_results=n_results)

    if operation in {"previous", "next"}:
        return retrieve_relative(entity, identifier, operation)

    if operation == "list_files":
        files = retrieve_all_changed_files()
        return {
            "ids": [[f"file_{index}" for index, _ in enumerate(files)]],
            "documents": [[file] for file in files],
            "metadatas": [[{"type": "file", "path": file}] for file in files],
        }

    return _build_result([])
