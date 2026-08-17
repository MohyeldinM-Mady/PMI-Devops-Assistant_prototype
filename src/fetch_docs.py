import json

from pathlib import Path
from src.config import DATA_DIR, validate_github_config
from src.github_client import get_repo


def fetch_docs():
    validate_github_config()
    repo = get_repo()
    queue = list(repo.get_contents(""))
    docs = []

    while queue:
        item = queue.pop(0)
        if item.type == "dir":
            queue.extend(repo.get_contents(item.path))
        elif item.name.lower().endswith(".md"):
            docs.append({
                "filename": item.name,
                "path": item.path,
                "content": item.decoded_content.decode("utf-8"),
            })

    return docs


def save_docs(docs, path=DATA_DIR / "docs.json"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=4, ensure_ascii=False)
