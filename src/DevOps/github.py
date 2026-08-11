import os

import requests


def get_changed_files(
    owner: str,
    repo: str,
    pr_number: int,
) -> list[dict]:
    token = os.getenv("GITHUB_TOKEN")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return [
        {
            "filename": file["filename"],
            "status": file["status"],
            "patch": file.get("patch", ""),
        }
        for file in response.json()
    ]

def post_pr_comment(
    owner: str,
    repo: str,
    pr_number: int,
    body: str,
) -> None:
    token = os.getenv("GITHUB_TOKEN")

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/issues/{pr_number}/comments"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.post(
        url,
        headers=headers,
        json={"body": body},
    )

    if not response.ok:
        print("=== GITHUB COMMENT ERROR ===")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

    response.raise_for_status()

    print("PMI analysis posted to PR successfully.")