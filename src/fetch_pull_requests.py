import json
import os
from src.github_client import get_repo

def fetch_pull_requests():
    """
    Pulls all pull requests from the repository and returns a list of dictionaries.
    """
    repo = get_repo()
    pulls = repo.get_pulls(state="all")
    pr_data_list = []

    for pr in pulls:
        pr_data = {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "author": pr.user.login if pr.user else None,
            "state": pr.state,
            "merged": pr.merged,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
            "linked_issues": [
                word.lstrip("#") for word in (pr.body or "").split()
                if word.lstrip("#").isdigit() and "#" in word
            ],
            "files_changed": [f.filename for f in pr.get_files()]
        }
        pr_data_list.append(pr_data)

    return pr_data_list

def save_pull_requests(prs, path="data/pull_requests.json"):
    """
    Writes the list of pull request dictionaries to a JSON file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(prs, f, indent=4, ensure_ascii=False)