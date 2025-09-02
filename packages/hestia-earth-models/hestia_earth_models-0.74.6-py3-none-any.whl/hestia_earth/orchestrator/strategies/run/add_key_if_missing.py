from hestia_earth.orchestrator.log import logShouldRun
from hestia_earth.orchestrator.utils import get_required_model_param


def should_run(data: dict, model: dict):
    key = get_required_model_param(model, 'key')
    run = data.get(key) is None
    logShouldRun(data, model.get('model'), None, run, key=key, value=model.get('value'))
    return run
