from datetime import datetime

from chance import chance

from git_timemachine.__main__ import app
from .helper import repo_add_new_file


def test_commit_on_empty_repo(empty_repo, runner, gtm_config, gtm_states):
    assert_new_commit(empty_repo, runner, gtm_config, gtm_states)


def test_commit_on_nonempty_repo(nonempty_repo, runner, gtm_config, gtm_states):
    assert_new_commit(nonempty_repo, runner, gtm_config, gtm_states)


def test_exception_nothing_to_commit(empty_repo, nonempty_repo, runner, gtm_config, gtm_states):
    for repo in [empty_repo, nonempty_repo]:
        result = runner.invoke(app, ['-C', repo.workdir, 'commit', '--message', chance.sentence()])

        assert result.exception
        assert 'Nothing to commit or pending changes.' in result.output


def test_exception_commit_earlier(nonempty_repo, runner, gtm_config, gtm_states):
    gtm_states.last_commit_time = datetime(2000, 1, 1, 8, 0, 0)
    gtm_states.save()

    repo_add_new_file(nonempty_repo)
    result = runner.invoke(app, ['-C', nonempty_repo.workdir, 'commit', '--message', chance.sentence()])

    assert result.exception
    assert 'Commit time is earlier than HEAD.' in result.output


def test_exception_daily_commit_limit(empty_repo, nonempty_repo, runner, gtm_config, gtm_states):
    gtm_config.max_daily_commits = 1
    gtm_config.save()

    for repo in [empty_repo, nonempty_repo]:
        repo_add_new_file(repo)

        result = runner.invoke(app, ['-C', repo.workdir, 'commit', '--message', chance.sentence()])
        assert not result.exception

        repo_add_new_file(repo)

        result = runner.invoke(app, ['-C', repo.workdir, 'commit', '--message', chance.sentence()])
        assert result.exception
        assert 'Exceeded the daily commit limit: 1' in result.output


def assert_new_commit(repo, runner, gtm_config, gtm_states):
    last_commit_time = gtm_states.last_commit_time

    if repo.head_is_unborn:
        commit_num = 0
        parent_id = None
    else:
        commits = list(repo.walk(repo.head.target))
        commit_num = len(commits)
        parent_id = str(commits[0].id)

    repo_add_new_file(repo)
    result = runner.invoke(app, ['-C', repo.workdir, 'commit', '--message', chance.sentence()])

    if result.exception:
        raise result.exception

    commits = list(repo.walk(repo.head.target))
    assert len(commits) == commit_num + 1

    new_commit = commits[0]
    if commit_num == 0:
        assert len(new_commit.parents) == 0
    else:
        assert str(new_commit.parents[0].id) == parent_id

    assert new_commit.author.name == new_commit.committer.name == repo.config['user.name']
    assert new_commit.author.email == new_commit.committer.email == repo.config['user.email']

    commit_range = range(gtm_config.min_seconds_increased - 1, gtm_config.max_seconds_increased + 1)
    assert int(new_commit.author.time - last_commit_time.timestamp()) in commit_range
