from git_timemachine.__main__ import app


def test_command_review(runner, gtm_config, gtm_states, nonempty_repo):
    result = runner.invoke(app, ['-C', nonempty_repo.workdir, 'review'])

    assert 'date    | commits |\n+------------+---------+\n| 2022-07-23 |    3' in result.output
