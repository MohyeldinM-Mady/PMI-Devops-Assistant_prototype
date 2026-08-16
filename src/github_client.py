from github import Github

from src.config import GITHUB_TOKEN, REPO_NAME, REPO_OWNER, validate_github_config


def get_repo():
    validate_github_config()
    return Github(GITHUB_TOKEN).get_repo(f"{REPO_OWNER}/{REPO_NAME}")
