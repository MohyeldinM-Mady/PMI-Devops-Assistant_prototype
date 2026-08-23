import json

from src.config import PROCESSED_DIR
from src.process_commits import process_commits
from src.process_docs import process_docs
from src.process_issues import process_issues
from src.process_pull_requests import process_pull_requests


def build_knowledge_base(output_path=PROCESSED_DIR / "knowledge_base.json"):
    processors = [
        ("commits", process_commits),
        ("issues", process_issues),
        ("pull requests", process_pull_requests),
        ("documentation", process_docs),
    ]

    all_documents = []
    for label, processor in processors:
        documents = processor()
        print(f"Processed {len(documents)} {label}.")
        all_documents.extend(documents)

    output_path = __import__("pathlib").Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_documents, f, indent=4, ensure_ascii=False)

    print(f"Knowledge base built: {len(all_documents)} total documents saved to {output_path}")
    return all_documents


if __name__ == "__main__":
    build_knowledge_base()
