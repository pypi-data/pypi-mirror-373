from datetime import datetime

import typer
from prettytable import PrettyTable
from pygit2 import Repository, discover_repository


def review_command(ctx: typer.Context):
    """
    Review the commits of repository.
    """

    repo_dir = ctx.obj['repo_dir']
    repo = Repository(discover_repository(str(repo_dir)))

    reports = {}
    for commit in repo.walk(repo.head.target):
        date_str = datetime.fromtimestamp(commit.commit_time).strftime('%Y-%m-%d')

        if date_str in reports:
            reports[date_str] += 1
        else:
            reports[date_str] = 1

    table = PrettyTable()
    table.field_names = ['date', 'commits']

    for key, value in reports.items():
        table.add_row([key, value])

    typer.echo(table)
