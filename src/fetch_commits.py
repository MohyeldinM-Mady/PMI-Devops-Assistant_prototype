import json

from src.config import DATA_DIR, validate_github_config
from src.github_client import get_repo


def fetch_commits():
    validate_github_config()
    repo = get_repo()
    return [
        {
            "sha": commit.sha,
            "author": commit.commit.author.name if commit.commit.author else None,
            "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
            "message": commit.commit.message,
            "files_changed": [file.filename for file in commit.files],
        }
        for commit in repo.get_commits()
    ]


def save_commits(commits, path=DATA_DIR / "commits.json"):
    path = __import__("pathlib").Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(commits, f, indent=4, ensure_ascii=False)
