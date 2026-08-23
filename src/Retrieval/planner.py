import re

from src.Retrieval.schema import QueryPlan


ENTITY_ALIASES = {
    "commit": "commit",
    "commits": "commit",
    "pr": "pull_request",
    "prs": "pull_request",
    "pull request": "pull_request",
    "pull requests": "pull_request",
    "issue": "issue",
    "issues": "issue",
    "doc": "doc",
    "docs": "doc",
    "documentation": "doc",
    "document": "doc",
}

# ============================================================
# Normalization
# ============================================================

def _normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("`", "")
    value = value.replace("_", " ")
    value = re.sub(r"\s+", " ", value)

    return value


def _normalize_filename(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("\\", "/")

    return value


# ============================================================
# Identifier helpers
# ============================================================

def _normalize_identifier(value: str) -> str:
    return value.strip().strip("`#.,")


def _explicit_entity_identifier(question: str):
    lowered = _normalize_text(question)

    commit = re.search(
        r"\bcommit\s+([0-9a-f]{7,40})\b",
        lowered,
    )

    if commit:
        return "commit", _normalize_identifier(commit.group(1))

    pr = re.search(
        r"\b(?:pr|pull\s+request)\s*#?\s*(\d+)\b",
        lowered,
    )

    if pr:
        return "pull_request", _normalize_identifier(pr.group(1))

    issue = re.search(
        r"\bissue\s*#?\s*(\d+)\b",
        lowered,
    )

    if issue:
        return "issue", _normalize_identifier(issue.group(1))

    doc = re.search(
        r"\b(?:[\w.-]+\.md|readme)\b",
        lowered,
        re.IGNORECASE,
    )

    if doc and any(
        word in lowered
        for word in (
            "read",
            "show",
            "display",
            "content",
            "explain",
            "open",
        )
    ):
        identifier = doc.group(0)

        if identifier == "readme":
            identifier = "readme.md"

        return "doc", _normalize_filename(identifier)

    return None, None

def _fields_for_question(question: str, entity: str) -> list[str]:
    lowered = _normalize_text(question)
    fields = []

    if "file" in lowered or "change" in lowered:
        fields.append("files_changed")
    if "author" in lowered or "who" in lowered:
        fields.append("author")
    if "date" in lowered or "when" in lowered:
        fields.append("date")
    if "message" in lowered:
        fields.append("message")
    if "title" in lowered:
        fields.append("title")
    if "status" in lowered or "state" in lowered:
        fields.append("state")
    if "merged" in lowered:
        fields.append("merged")
    if "label" in lowered:
        fields.append("labels")
    if "content" in lowered or "read" in lowered:
        fields.append("full_content")

    if fields:
        return fields

    return {
        "commit": ["sha", "author", "date", "message", "files_changed"],
        "pull_request": ["number", "title", "author", "date", "state", "merged", "files_changed"],
        "issue": ["number", "title", "author", "date", "state", "labels"],
        "doc": ["filename", "path", "full_content"],
    }.get(entity, [])


def _explicit_list_entity(question: str):
    lowered = _normalize_text(question)
    if not any(word in lowered for word in ("all", "every", "list", "show")):
        return None

    if "changed files" in lowered or "files changed" in lowered:
        return "list_files"

    for phrase, entity in sorted(ENTITY_ALIASES.items(), key=lambda item: -len(item[0])):
        pattern = rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])"
        if re.search(pattern, lowered):
            return entity

    if "documentation files" in lowered or "doc files" in lowered:
        return "doc"

    return None


def _deterministic_plan(question: str, active_reference: dict | None):
    lowered = _normalize_text(question)
    active_reference = active_reference or {}

        # Explicit first/latest record requests
    if any(word in lowered for word in ("first", "earliest", "oldest")):
        for phrase, entity in sorted(
            ENTITY_ALIASES.items(),
            key=lambda item: -len(item[0]),
        ):
            pattern = rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])"

            if re.search(pattern, lowered):
                return QueryPlan(
                    entity=entity,
                    operation="first",
                    fields=_fields_for_question(question, entity),
                    query=question,
                    reference_source="none",
                )

    if any(word in lowered for word in ("last", "latest", "newest", "most recent")):
        for phrase, entity in sorted(
            ENTITY_ALIASES.items(),
            key=lambda item: -len(item[0]),
        ):
            pattern = rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])"

            if re.search(pattern, lowered):
                return QueryPlan(
                    entity=entity,
                    operation="last",
                    fields=_fields_for_question(question, entity),
                    query=question,
                    reference_source="none",
                )

    explicit_entity, explicit_identifier = _explicit_entity_identifier(question)

    if explicit_entity:
        if "previous" in lowered or "before" in lowered:
            operation = "previous"
        elif "next" in lowered or "after" in lowered:
            operation = "next"
        else:
            operation = "get"

        return QueryPlan(
            entity=explicit_entity,
            operation=operation,
            identifier=explicit_identifier,
            fields=_fields_for_question(question, explicit_entity),
            query=question,
            reference_source="explicit",
        )

    if any(word in lowered for word in ("previous", "before", "next", "after")):
        if active_reference.get("entity") and active_reference.get("identifier"):
            operation = "previous" if any(
                word in lowered for word in ("previous", "before")
            ) else "next"
            return QueryPlan(
                entity=active_reference["entity"],
                operation=operation,
                identifier=str(active_reference["identifier"]),
                fields=[],
                query=question,
                reference_source="active",
            )
    if "first" in lowered and "commit" in lowered:
        return QueryPlan(
            entity="commit",
            operation="first",
            identifier=None,
            fields=_fields_for_question(question, "commit"),
            query=question,
            reference_source="explicit",
        )

    if "last" in lowered and "commit" in lowered:
        return QueryPlan(
            entity="commit",
            operation="last",
            identifier=None,
            fields=_fields_for_question(question, "commit"),
            query=question,
            reference_source="explicit",
        )

    list_entity = _explicit_list_entity(question)
    if list_entity:
        if list_entity == "list_files":
            return QueryPlan(
                entity="unknown",
                operation="list_files",
                fields=["files_changed"],
                query=question,
                reference_source="none",
            )

        fields = {
            "commit": ["sha", "author", "date", "message", "files_changed"],
            "pull_request": ["number", "title", "author", "date", "state", "merged", "files_changed"],
            "issue": ["number", "title", "author", "date", "state", "labels"],
            "doc": ["filename", "path"],
        }.get(list_entity, [])
        return QueryPlan(
            entity=list_entity,
            operation="list",
            fields=fields,
            query=question,
            reference_source="none",
        )

    if active_reference and active_reference.get("entity") and active_reference.get("identifier"):
        if any(
            token in lowered
            for token in (
                "it", "this", "that", "its", "the file", "the files",
                "the author", "the title", "the date", "what did it",
            )
        ):
            # Explicit follow-ups about a known field stay deterministic.
            field_question = any(
                marker in lowered
                for marker in (
                    "file", "change", "author", "who", "date", "when", "message",
                    "title", "status", "state", "merged", "label",
                )
            )
            if field_question:
                return QueryPlan(
                    entity=active_reference["entity"],
                    operation="get",
                    identifier=str(active_reference["identifier"]),
                    fields=_fields_for_question(question, active_reference["entity"]),
                    query=question,
                    reference_source="active",
                )
            # Semantic follow-ups remain searches, but the active entity is
            # included in the retrieval query so the exact referenced record
            # has a strong lexical signal without invoking another planner LLM.
            scoped_query = (
                f"{active_reference['entity']} {active_reference['identifier']} {question}"
            )
            return QueryPlan(
                entity="unknown",
                operation="search",
                identifier=None,
                fields=[],
                query=scoped_query,
                reference_source="active",
            )

    return None


def plan_query(question: str, active_reference: dict | None = None) -> dict:
    """Build a retrieval plan without an inference call.

    Structured questions are routed deterministically. Everything else is a
    semantic search. This prevents an LLM planner from hallucinating a
    structured operation (for example, turning a conceptual question into
    ``list pull requests``) and removes one inference request per semantic
    query.
    """
    deterministic = _deterministic_plan(question, active_reference)
    if deterministic:
        result = deterministic.sanitized(question).model_dump()
        print("QUERY PLAN:", result, flush=True)
        return result

    result = QueryPlan(
        entity="unknown",
        operation="search",
        identifier=None,
        fields=[],
        query=question,
        reference_source="none",
    ).sanitized(question).model_dump()

    print("QUERY PLAN:", result, flush=True)

    return result
