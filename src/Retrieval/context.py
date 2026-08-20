import json


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def build_context(results, fields=None, entity=None, scope=None):
    fields = fields or []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    context_parts = []

    for document_id, document, metadata in zip(ids, documents, metadatas):
        lines = [f"[{metadata.get('type', 'unknown').upper()}]", f"ID: {document_id}"]

        scalar_fields = {
            "sha": "SHA", "number": "Number", "author": "Author", "date": "Date",
            "message": "Message", "title": "Title", "state": "State", "merged": "Merged",
            "filename": "Filename", "path": "Path",
        }
        for field, label in scalar_fields.items():
            if field in fields and field in metadata:
                lines.append(f"{label}: {metadata[field]}")

        if "full_content" in fields:
            lines.append(f"FULL CONTENT:\n{metadata.get('full_content', 'No content available')}")

        if "labels" in fields:
            labels = _as_list(metadata.get("labels"))
            if labels:
                lines.append("LABELS:\n" + "\n".join(f"- {label}" for label in labels))

        if "files_changed" in fields:
            files = _as_list(metadata.get("files_changed"))
            if files:
                lines.append("CHANGED FILES:\n" + "\n".join(f"- {file}" for file in files))

        if "linked_issues" in fields:
            issues = _as_list(metadata.get("linked_issues"))
            if issues:
                lines.append("LINKED ISSUES:\n" + "\n".join(f"- {issue}" for issue in issues))

        # Semantic search over documentation needs the full source content.
        # The indexed metadata keeps full_content even when an older index
        # still contains a shortened document text.
        content = document
        if scope == "search" and metadata.get("type") == "doc":
            content = metadata.get("full_content") or document

        lines.append(f"CONTENT:\n{content}")
        context_parts.append("\n".join(lines))

    return "\n\n---\n\n".join(context_parts)
