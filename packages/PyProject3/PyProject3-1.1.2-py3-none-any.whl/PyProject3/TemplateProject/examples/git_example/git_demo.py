import git

repo = git.Git(r'/')
# repo.checkout('debug')
s = repo.status()
print(s)
# 所有git支持的命令这里都支持
