def build_context(results):
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    context_parts = []

    for document_id, document, metadata in zip(
        ids,
        documents,
        metadatas,
    ):
        context_parts.append(
            f"[{metadata.get('type', 'unknown').upper()}]\n"
            f"ID: {document_id}\n"
            f"Author: {metadata.get('author', 'unknown')}\n"
            f"Date: {metadata.get('date', 'unknown')}\n"
            f"Content:\n{document}"
        )

    return "\n\n---\n\n".join(context_parts)