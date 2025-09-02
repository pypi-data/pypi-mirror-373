from hestia_earth.orchestrator.strategies.run.add_key_if_missing import should_run


def test_should_run():
    data = {}
    key = 'model-key'
    model = {'key': key}

    # key not in data => run
    assert should_run(data, model) is True

    # key in data => no run
    data[key] = 10
    assert not should_run(data, model)
