import git
from pathlib import Path

def is_git_repo(path):
    """Determine whether the path is a Git repo"""
    try:
        _ = git.Repo(path).git_dir
        return path
    except git.exc.InvalidGitRepositoryError:
        return False


def get_git_repo(starting_dir: Path = None):
    """Finds the Git repo location (folder) if a given file is within one, however deep"""

    if starting_dir is not None:
        p = starting_dir
    else:
        p = Path.cwd().resolve()

    if p == Path("/"):
        return None

    if is_git_repo(p):
        return p
    else:
        return get_git_repo(p.parent.resolve())


def get_tag_or_commit(only_commit=False):
    """Gets a file's Git commit or Tag. Can be forced to get only the commit"""
    repo = git.Repo(get_git_repo())
    if only_commit:
        return repo.heads.master.commit

    if repo.tags:
        return repo.tags[0]
    else:
        return repo.heads.master.commit


def get_repo_uri():
    """Gets the URI of a file's repo's origin"""
    repo_dir = get_git_repo()
    if repo_dir is None:
        return None
    repo = git.Repo(repo_dir)
    origin_uri_with_user = repo.remotes.origin.url
    if origin_uri_with_user.find("@") >= 0:
        origin_uri_with_user = "https://" + origin_uri_with_user.split("@")[1]
    return origin_uri_with_user


def get_version_uri():
    """Gets the URI of a file's origin's commit or tag"""
    repo_uri = get_repo_uri()
    if repo_uri is None:
        return None
    id_ = str(get_tag_or_commit())

    if "bitbucket" in repo_uri:
        if len(id_) < 10:  # tag
            path = "/commits/tag/"
        else:  # commit
            path = "/commits/"
    elif "github" in repo_uri:
        if len(id_) < 10:  # tag
            path = "/releases/tag/"
        else:  # commit
            path = "/commit/"
    # TODO: David to add
    # elif "??" in repo_uri: # CodeCommit
    #     pass
    else:
        raise Exception("Only GitHub & BitBucket repos are supported")

    return repo_uri.replace(".git", "") + path + id_