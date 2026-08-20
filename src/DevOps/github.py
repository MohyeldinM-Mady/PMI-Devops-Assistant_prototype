import os

import requests


API_BASE = "https://api.github.com"


def _headers():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_changed_files(owner: str, repo: str, pr_number: int) -> list[dict]:
    url = f"{API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=_headers(), timeout=30)
    response.raise_for_status()
    return [
        {
            "filename": file["filename"],
            "status": file["status"],
            "patch": file.get("patch", ""),
        }
        for file in response.json()
    ]


def post_pr_comment(owner: str, repo: str, pr_number: int, body: str) -> None:
    url = f"{API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    response = requests.post(
        url,
        headers=_headers(),
        json={"body": body},
        timeout=30,
    )
    response.raise_for_status()
