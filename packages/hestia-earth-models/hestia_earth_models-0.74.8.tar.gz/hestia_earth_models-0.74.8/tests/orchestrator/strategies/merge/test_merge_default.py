from hestia_earth.orchestrator.strategies.merge.merge_default import merge


def test_should_merge():
    source = {'value': [100]}
    dest = {'value': [50]}
    assert merge(source, dest) == dest
