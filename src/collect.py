from src.fetch_commits import fetch_commits, save_commits
from src.fetch_docs import fetch_docs, save_docs
from src.fetch_issues import fetch_issues, save_issues
from src.fetch_pull_requests import fetch_pull_requests, save_pull_requests


def main():
    print("Starting PMI Data Collection (Phase 1)...")

    commits = fetch_commits()
    save_commits(commits)
    print(f"Fetched {len(commits)} commits.")

    issues = fetch_issues()
    save_issues(issues)
    print(f"Fetched {len(issues)} issues.")

    pull_requests = fetch_pull_requests()
    save_pull_requests(pull_requests)
    print(f"Fetched {len(pull_requests)} pull requests.")

    docs = fetch_docs()
    save_docs(docs)
    print(f"Fetched {len(docs)} documentation files.")

    print("Data collection completed.")


if __name__ == "__main__":
    main()
