import json
import re

from pathlib import Path
from src.config import DATA_DIR, validate_github_config
from src.github_client import get_repo


def fetch_issues():
    validate_github_config()
    repo = get_repo()
    issue_data = []

    for issue in repo.get_issues(state="all"):
        # GitHub exposes pull requests through the issues endpoint too.
        if issue.pull_request is not None:
            continue

        issue_data.append({
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "labels": [label.name for label in issue.labels],
            "state": issue.state,
            "author": issue.user.login if issue.user else None,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            "comments": issue.comments,
        })

    return issue_data


def save_issues(issues, path=DATA_DIR / "issues.json"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=4, ensure_ascii=False)
