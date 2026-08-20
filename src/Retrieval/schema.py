from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Entity = Literal["commit", "issue", "pull_request", "doc", "unknown"]
Operation = Literal[
    "get",
    "list",
    "search",
    "previous",
    "next",
    "list_files",
]

SUPPORTED_FIELDS = {
    "sha",
    "number",
    "author",
    "date",
    "message",
    "files_changed",
    "title",
    "state",
    "merged",
    "linked_issues",
    "filename",
    "path",
    "full_content",
    "labels",
}


class QueryPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entity: Entity = "unknown"
    operation: Operation = "search"
    identifier: str | None = None
    fields: list[str] = Field(default_factory=list)
    query: str = ""
    reference_source: Literal["explicit", "active", "none"] = "none"

    def sanitized(self, question: str) -> "QueryPlan":
        self.identifier = str(self.identifier) if self.identifier is not None else None
        self.fields = [field for field in self.fields if field in SUPPORTED_FIELDS]
        self.query = self.query.strip() or question
        return self
