import json
import os
from src.github_client import get_repo

def fetch_commits():
    """
    Pulls all commits from the repository and returns a list of dictionaries.
    """
    repo = get_repo()
    commits = repo.get_commits()
    commit_data_list = []

    for commit in commits:
        commit_data = {
            "sha": commit.sha,
            "author": commit.commit.author.name if commit.commit.author else None,
            "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
            "message": commit.commit.message,
            "files_changed": [f.filename for f in commit.files]
        }
        commit_data_list.append(commit_data)

    return commit_data_list

def save_commits(commits, path="data/commits.json"):
    """
    Writes the list of commit dictionaries to a JSON file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(commits, f, indent=4, ensure_ascii=False)
