import os
import json
from enum import Enum
from hestia_earth.utils.tools import flatten

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class AWARE_VERSION(Enum):
    V1 = '1.2'
    V2 = '2.0'


def _is_aggregated_model(model: dict):
    return isinstance(model, dict) and 'aggregated' in model.get('value', '').lower()


def _remove_aggregated(models: list):
    values = [
        _remove_aggregated(m) if isinstance(m, list) else m if not _is_aggregated_model(m) else None
        for m in models
    ]
    return list(filter(lambda v: v is not None, values))


def _use_aware_1(models: list):
    return [
        _use_aware_1(m) if isinstance(m, list) else
        m | {'model': 'aware'} if m.get('model') == 'aware2-0' else
        m | {'value': 'awareWaterBasinId_v1'} if m.get('value') == 'awareWaterBasinId' else
        m
        for m in models
    ]


def _load_config(filename: str) -> dict:
    with open(os.path.join(CURRENT_DIR, f"{filename}.json"), 'r') as f:
        return json.load(f)


def load_config(
    node_type: str,
    skip_aggregated_models: bool = False,
    use_aware_version: AWARE_VERSION = AWARE_VERSION.V2
) -> dict:
    """
    Load the configuration associated with the Node Type.

    Parameters
    ----------
    node_type : str
        The Node Type to load configuration. Can be: `Cycle`, `Site`, `ImpactAssessment`.
    skip_aggregated_models : bool
        Include models using aggregated data. Included by default.
    use_aware_version : AWARE_VERSION
        Choose which AWARE version to use. Defaults to using version `2.0`.
    """
    try:
        config = _load_config(node_type)
        models = config.get('models')
        models = _remove_aggregated(models) if skip_aggregated_models else models
        models = _use_aware_1(models) if use_aware_version == AWARE_VERSION.V1 else models
        return config | {'models': models}
    except FileNotFoundError:
        raise Exception(f"Invalid type {node_type}.")


def config_max_stage(config: dict):
    """
    Get maximum `stage` value from a configuration.

    Parameters
    ----------
    config : dict
        The Node configuration.
    """
    models = config.get('models', [])
    return max([m.get('stage', 1) for m in flatten(models)])


def _load_stage_config(filename: str, node_type: str, stage: int):
    config = _load_config(filename).get(node_type, {})

    if f"stage-{stage}" not in config:
        raise Exception(f"Invalid stage configuration for {node_type}: {stage}")

    return config.get(f"stage-{stage}", [])


def load_run_config(node_type: str, stage: int):
    return _load_stage_config('run-calculations', node_type, stage)


def load_trigger_config(node_type: str, stage: int):
    return _load_stage_config('trigger-calculations', node_type, stage)


def get_max_stage(node_type: str):
    config = _load_config('run-calculations').get(node_type, {})
    stages = list(map(lambda k: int(k.replace('stage-', '')), config.keys()))
    return max(stages)
