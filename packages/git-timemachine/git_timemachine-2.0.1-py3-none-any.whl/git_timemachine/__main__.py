import os
from pathlib import Path

import typer

from git_timemachine.commands import advance, commit, review
from git_timemachine.models import Config, States

app = typer.Typer(no_args_is_help=True)
app.command(name='advance')(advance.advance_command)
app.command(name='commit')(commit.commit_command)
app.command(name='review')(review.review_command)


@app.callback()
def main(
    ctx: typer.Context,
    repo_dir: Path = typer.Option(Path.cwd(), '--repo-dir', '-C', help='Path of repository directory.', metavar='PATH'),
):
    """
    A command-line tool that helps you record commits on Git repositories at any time node.
    """

    config_file = Path(os.getenv('GIT_TIMEMACHINE_CONFIG', Path.home() / '.git-timemachine' / 'config'))
    states_file = Path(os.getenv('GIT_TIMEMACHINE_STATES', Path.home() / '.git-timemachine' / 'states'))

    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        Config().save(config_file)

    if not states_file.exists():
        states_file.parent.mkdir(parents=True, exist_ok=True)
        States().save(states_file)

    ctx.ensure_object(dict)

    ctx.obj['repo_dir'] = repo_dir
    ctx.obj['config'] = Config.load(config_file)
    ctx.obj['states'] = States.load(states_file)


if __name__ == '__main__':
    app()
