import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

if not GITHUB_TOKEN or not REPO_OWNER or not REPO_NAME:
    raise EnvironmentError("Missing required environment variables. Please ensure GITHUB_TOKEN, REPO_OWNER, and REPO_NAME are set in .env")
