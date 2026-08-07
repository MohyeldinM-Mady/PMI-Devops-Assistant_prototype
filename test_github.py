from github import Github

g = Github()
repo = g.get_repo("octocat/Hello-World")
commits = repo.get_commits()
commit = commits[0]
print(type(commit.commit.author.date))
