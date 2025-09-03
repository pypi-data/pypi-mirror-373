from git_timemachine.__main__ import app
from git_timemachine.models import States


def test_advance_command(runner, gtm_config, gtm_states):
    path = gtm_states._path
    last_commit_time = gtm_states.last_commit_time

    result = runner.invoke(app, ['advance', '--days', '3', '--hour', '20'])
    assert not result.exception

    gtm_states = States.load(path)
    assert gtm_states.last_commit_time.day - last_commit_time.day == 3
    assert gtm_states.last_commit_time.hour == 20
