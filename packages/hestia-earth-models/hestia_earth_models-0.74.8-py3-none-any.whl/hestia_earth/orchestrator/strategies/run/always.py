from hestia_earth.orchestrator.log import logShouldRun


def should_run(data: dict, model: dict):
    logShouldRun(data, model.get('model'), None, True, key=model.get('key'), value=model.get('value'))
    return True
