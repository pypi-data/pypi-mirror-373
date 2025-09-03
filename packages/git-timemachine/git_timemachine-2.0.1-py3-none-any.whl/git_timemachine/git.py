import os
import subprocess
from datetime import datetime

from pygit2 import Repository, GIT_STATUS_WT_NEW, GitError


def git_external_commit(repo: Repository, args: list[str], commit_time: datetime):
    env = commit_time.replace(microsecond=0).astimezone().isoformat()
    subprocess.run(
        ['git', '-C', repo.workdir, 'commit'] + list(args),
        cwd=repo.workdir,
        env={**os.environ, 'GIT_AUTHOR_DATE': env, 'GIT_COMMITTER_DATE': env},
        check=True
    )


def check_repo_max_daily_commits(repo: Repository, commit_time: datetime, max_num: int):
    if repo.head_is_unborn or max_num == 0:
        return

    date_str = commit_time.strftime('%Y-%m-%d')

    commits = [commit for commit in repo.walk(repo.head.target) if datetime.fromtimestamp(commit.commit_time).strftime('%Y-%m-%d') == date_str]

    if len(commits) >= max_num:
        raise GitError(f'Exceeded the daily commit limit: {max_num}.')


def check_repo_commit_time(repo: Repository, commit_time: datetime):
    if not repo.head_is_unborn and commit_time.timestamp() < next(repo.walk(repo.head.target)).commit_time:
        raise GitError('Commit time is earlier than HEAD.')


def check_repo_commit_status(repo: Repository):
    repo_status = repo.status(untracked_files='no')
    if repo_status == {} or len([value for value in repo_status.values() if value < GIT_STATUS_WT_NEW]) < 1:
        raise GitError('Nothing to commit or pending changes.')
