from hestia_earth.orchestrator.strategies.run.always import should_run


def test_should_run():
    assert should_run({}, {}) is True
