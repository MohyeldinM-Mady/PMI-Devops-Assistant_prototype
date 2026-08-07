from github import Github
from src.config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME

def get_repo():
    """
    Authenticates with GitHub using the provided token and returns the target repository.
    """
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    return repo
