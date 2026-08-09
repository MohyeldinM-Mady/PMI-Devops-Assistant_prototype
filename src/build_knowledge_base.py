import json
import os

from src.process_commits import process_commits
from src.process_issues import process_issues
from src.process_pull_requests import process_pull_requests
from src.process_docs import process_docs


def build_knowledge_base(output_path="data/processed/knowledge_base.json"):
    """
    Runs all processors, combines their output into a single list of
    knowledge documents, and saves the result as the Phase 2 deliverable.
    """
    all_documents = []

    print("Processing commits...")
    commit_docs = process_commits()
    print(f"Processed {len(commit_docs)} commits.")
    all_documents.extend(commit_docs)

    print("Processing issues...")
    issue_docs = process_issues()
    print(f"Processed {len(issue_docs)} issues.")
    all_documents.extend(issue_docs)

    print("Processing pull requests...")
    pr_docs = process_pull_requests()
    print(f"Processed {len(pr_docs)} pull requests.")
    all_documents.extend(pr_docs)

    print("Processing docs...")
    doc_docs = process_docs()
    print(f"Processed {len(doc_docs)} documentation files.")
    all_documents.extend(doc_docs)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_documents, f, indent=4, ensure_ascii=False)

    print(f"Knowledge base built: {len(all_documents)} total documents saved to {output_path}")
    return all_documents


if __name__ == "__main__":
    build_knowledge_base()
