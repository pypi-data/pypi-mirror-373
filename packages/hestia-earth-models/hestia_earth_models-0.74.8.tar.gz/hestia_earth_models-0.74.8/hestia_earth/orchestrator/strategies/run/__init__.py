import importlib

from hestia_earth.orchestrator.utils import get_required_model_param


def should_run(data: dict, model: dict):
    strategy = get_required_model_param(model, 'runStrategy')
    return importlib.import_module(f"hestia_earth.orchestrator.strategies.run.{strategy}").should_run(data, model)
