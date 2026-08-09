import json
import os
from src.github_client import get_repo

def fetch_issues():
    """
    Pulls all issues from the repository and returns a list of dictionaries.
    Note: GitHub's API treats pull requests as a type of issue, so we
    explicitly skip any issue that has a `pull_request` attribute set.
    """
    repo = get_repo()
    issues = repo.get_issues(state="all")
    issue_data_list = []

    for issue in issues:
        # Skip PRs — the GitHub API returns them mixed in with issues
        if issue.pull_request is not None:
            continue

        issue_data = {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "labels": [label.name for label in issue.labels],
            "state": issue.state,
            "author": issue.user.login if issue.user else None,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            "comments": issue.comments
        }
        issue_data_list.append(issue_data)

    return issue_data_list

def save_issues(issues, path="data/issues.json"):
    """
    Writes the list of issue dictionaries to a JSON file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=4, ensure_ascii=False)