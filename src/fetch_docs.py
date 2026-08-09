import json
import os
from src.github_client import get_repo

def fetch_docs():
    """
    Walks the repository tree and pulls the content of all markdown (.md) files.
    Returns a list of dictionaries with filename, path, and raw content.
    """
    repo = get_repo()
    contents = repo.get_contents("")
    doc_data_list = []

    while contents:
        item = contents.pop(0)
        if item.type == "dir":
            contents.extend(repo.get_contents(item.path))
        elif item.name.lower().endswith(".md"):
            doc_data = {
                "filename": item.name,
                "path": item.path,
                "content": item.decoded_content.decode("utf-8")
            }
            doc_data_list.append(doc_data)

    return doc_data_list

def save_docs(docs, path="data/docs.json"):
    """
    Writes the list of document dictionaries to a JSON file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=4, ensure_ascii=False)