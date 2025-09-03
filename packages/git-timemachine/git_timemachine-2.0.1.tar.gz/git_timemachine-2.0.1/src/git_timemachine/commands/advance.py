from datetime import timedelta

import typer


def advance_command(
    ctx: typer.Context,
    days: int = typer.Option(1, '--days', '-d', help='Days to be advanced.'),
    hour: int = typer.Option(10, '--hour', '-h', help='Hour to start with.')
):
    """
    Advance the commit time by a given number of days and hours.
    """

    states = ctx.obj['states']

    commit_time = states.last_commit_time + timedelta(hours=days * 24)
    states.last_commit_time = commit_time.replace(hour=hour, minute=0, second=0, microsecond=0)
    states.save()
