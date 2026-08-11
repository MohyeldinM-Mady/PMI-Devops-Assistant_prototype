import os

from src.DevOps.github import get_changed_files
from src.DevOps.retrieval import retrieve_historical_context
from src.DevOps.analyzer import analyze_pull_request


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])

    owner, repo = repository.split("/")

    files = get_changed_files(owner, repo, pr_number)

    print(f"Changed files: {len(files)}")

    historical_context = retrieve_historical_context(files)

    print("\n=== Historical Context ===")
    print(historical_context)

    print("\n=== PMI AI Analysis ===")

    analysis = analyze_pull_request(
        files,
        historical_context,
    )

    print(analysis)


if __name__ == "__main__":
    main()