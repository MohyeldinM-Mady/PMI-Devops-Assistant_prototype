import json
import re

from src.config import DATA_DIR, validate_github_config
from src.github_client import get_repo


ISSUE_REFERENCE_PATTERN = re.compile(r"(?<!\w)#(\d+)\b")


def fetch_pull_requests():
    validate_github_config()
    repo = get_repo()
    pr_data = []

    for pr in repo.get_pulls(state="all"):
        pr_data.append({
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "author": pr.user.login if pr.user else None,
            "state": pr.state,
            "merged": pr.merged,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
            "linked_issues": ISSUE_REFERENCE_PATTERN.findall(pr.body or ""),
            "files_changed": [file.filename for file in pr.get_files()],
        })

    return pr_data


def save_pull_requests(prs, path=DATA_DIR / "pull_requests.json"):
    path = __import__("pathlib").Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(prs, f, indent=4, ensure_ascii=False)
