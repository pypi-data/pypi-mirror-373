import random
from datetime import timedelta

import typer
from pygit2 import Repository, GitError, discover_repository

from git_timemachine.git import (
    check_repo_commit_time,
    check_repo_commit_status,
    check_repo_max_daily_commits,
    git_external_commit
)


def commit_command(
    ctx: typer.Context,
    message: str = typer.Option(..., '--message', '-m', help='Message describing the commit'),
    args: list[str] = typer.Argument(None, help='Extra arguments to pass to git commit command')
):
    """
    Record a commit on repository at the specified time node.
    """

    repo_dir = ctx.obj['repo_dir']
    config = ctx.obj['config']
    states = ctx.obj['states']

    commit_time = states.last_commit_time
    repo = Repository(discover_repository(repo_dir))

    try:
        check_repo_commit_time(repo, commit_time)
        check_repo_commit_status(repo)
        check_repo_max_daily_commits(repo, commit_time, config.max_daily_commits)
    except GitError as exc:
        ctx.fail(str(exc))

    random.seed()

    commit_time += timedelta(seconds=random.randint(config.min_seconds_increased, config.max_seconds_increased))

    git_external_commit(repo, ['--message', message] + (args or []), commit_time)

    states.last_commit_time = commit_time
    states.save()
