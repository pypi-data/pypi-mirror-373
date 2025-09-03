import os
import shutil
import tarfile
import tempfile
from pathlib import Path

import pytest
from chance import chance
from pygit2 import discover_repository, Repository
from typer.testing import CliRunner

from git_timemachine.models import Config, States


def copy_asset(filename: str, path: Path):
    dest_path = path / filename
    shutil.copy(Path(__file__).parent / 'assets' / filename, dest_path)

    return dest_path


def extract_repo(filename: str, target: str):
    with tarfile.open(Path(__file__).parent.joinpath('assets', filename)) as tar:
        tar.extractall(target, filter='data')


@pytest.fixture(scope='function')
def temp_dir() -> Path:
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture(scope='function')
def empty_repo() -> Repository:
    with tempfile.TemporaryDirectory() as td:
        extract_repo('empty-repo.tar.gz', td)
        yield Repository(discover_repository(td))


@pytest.fixture(scope='function')
def nonempty_repo() -> Repository:
    with tempfile.TemporaryDirectory() as td:
        extract_repo('nonempty-repo.tar.gz', td)
        yield Repository(discover_repository(td))


@pytest.fixture(scope='module')
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope='function')
def gtm_config() -> Config:
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as file:
        max_daily_commits = 5
        min_seconds_increased = 600
        max_seconds_increased = 3600

        file.write(f'max_daily_commits: {max_daily_commits}\nmin_seconds_increased: {min_seconds_increased}\nmax_seconds_increased: {max_seconds_increased}\n')
        file.flush()

        os.environ['GIT_TIMEMACHINE_CONFIG'] = file.name

        yield Config.load(Path(file.name))

        file.close()
        os.unlink(file.name)


@pytest.fixture(scope='function')
def gtm_states() -> States:
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as file:
        last_commit_time = chance.date(2023, 1, 1).astimezone().strftime('%Y-%m-%dT%H:%M:%S')

        file.write(f'last_commit_time: {last_commit_time}')
        file.flush()

        os.environ['GIT_TIMEMACHINE_STATES'] = file.name

        yield States.load(Path(file.name))

        file.close()
        os.unlink(file.name)
