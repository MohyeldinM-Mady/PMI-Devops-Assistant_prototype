import os

from src.DevOps.github import get_changed_files
from src.DevOps.retrieval import retrieve_historical_context


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])

    owner, repo = repository.split("/")

    files = get_changed_files(owner, repo, pr_number)

    print(f"Changed files: {len(files)}")

    for file in files:
        print(f"\nFile: {file['filename']}")
        print(f"Status: {file['status']}")
        print(f"Patch:\n{file['patch']}")

    print("\n=== Historical Context ===")

    context = retrieve_historical_context(files)

    print(context)


if __name__ == "__main__":
    main()