from src.fetch_commits import fetch_commits, save_commits
from src.fetch_issues import fetch_issues, save_issues
from src.fetch_pull_requests import fetch_pull_requests, save_pull_requests
from src.fetch_docs import fetch_docs, save_docs

def main():
    print("Starting PMI Data Collection (Phase 1)...")
    
    print("Fetching commits...")
    commits = fetch_commits()
    print(f"Fetched {len(commits)} commits.")
    save_commits(commits)
    
    # TODO: Implement and uncomment when fetch_issues is ready
    # print("Fetching issues...")
    # issues = fetch_issues()
    # print(f"Fetched {len(issues)} issues.")
    # save_issues(issues)
    
    # TODO: Implement and uncomment when fetch_pull_requests is ready
    # print("Fetching pull requests...")
    # prs = fetch_pull_requests()
    # print(f"Fetched {len(prs)} pull requests.")
    # save_pull_requests(prs)
    
    # TODO: Implement and uncomment when fetch_docs is ready
    # print("Fetching docs...")
    # docs = fetch_docs()
    # print(f"Fetched {len(docs)} documents.")
    # save_docs(docs)

    print("Data collection completed.")

if __name__ == "__main__":
    main()
