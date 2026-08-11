import os

from src.DevOps.github import get_changed_files


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


if __name__ == "__main__":
    main()