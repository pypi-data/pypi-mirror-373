import os
import resource
import platform
from typing import Union, List
import importlib
from functools import reduce
import concurrent.futures
from copy import deepcopy
from hestia_earth.utils.tools import non_empty_list, current_time_ms

from hestia_earth.models.version import VERSION
from hestia_earth.orchestrator.log import logger
from hestia_earth.orchestrator.utils import get_required_model_param, _snakecase, reset_index
from hestia_earth.orchestrator.strategies.run import should_run
from hestia_earth.orchestrator.strategies.merge import merge


def _memory_usage():
    factor = 1024 * (
        1024 if platform.system() in ['Darwin', 'Windows'] else 1
    )
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / factor


def _max_workers(type: str):
    try:
        return int(os.getenv(f"MAX_WORKERS_{type.upper()}"))
    except Exception:
        return None


# do not deep copy to improve performance, only set on low risk keys
_SKIP_DEEPCOPY_KEYS = [
    'emissions',
    'emissionsResourceUse'
]


def _node_copy(node: dict):
    skip_keys = [key for key in _SKIP_DEEPCOPY_KEYS if key in node and isinstance(node[key], list)]
    new_node = deepcopy(node | {
        key: [] for key in skip_keys
    }) | {
        key: node[key] for key in skip_keys
    }
    return new_node


def _list_except_item(list, item):
    idx = list.index(item)
    return list[:idx] + list[idx+1:]


def _filter_models_stage(models: list, stage: Union[int, List[int]] = None):
    stages = stage if isinstance(stage, list) else [stage] if stage is not None else None
    return models if stage is None else non_empty_list([
        (_filter_models_stage(m, stage) if isinstance(m, list) else m) for m in models if (
            not isinstance(m, dict) or m.get('stage') in stages
        )
    ])


def _import_model(name: str):
    # try to load the model from the default hestia engine, fallback to orchestrator model
    try:
        return {
            'run': importlib.import_module(f"hestia_earth.models.{name}").run,
            'version': VERSION
        }
    except ModuleNotFoundError:
        # try to load the model from the the models folder, fallback to fully specified name
        try:
            return {
                'run': importlib.import_module(f"hestia_earth.orchestrator.models.{name}").run,
                'version': VERSION
            }
        except ModuleNotFoundError:
            return {
                'run': importlib.import_module(f"{name}").run,
                'version': VERSION
            }


def _run_pre_checks(data: dict):
    node_type = _snakecase(data.get('@type', data.get('type')))

    now = current_time_ms()
    memory_usage = _memory_usage()

    try:
        pre_checks = _import_model('.'.join([node_type, 'pre_checks'])).get('run')
        logger.info('running pre checks for %s', node_type)
        data = pre_checks(data)
    except Exception:
        pass

    logger.info('model_model=%s, model_value=%s, time=%s, memory_used=%s',
                node_type, 'pre_checks', current_time_ms() - now, _memory_usage() - memory_usage)

    return data


def _run_post_checks(data: dict):
    node_type = _snakecase(data.get('@type', data.get('type')))

    now = current_time_ms()
    memory_usage = _memory_usage()

    try:
        post_checks = _import_model('.'.join([node_type, 'post_checks'])).get('run')
        logger.info('running post checks for %s', node_type)
        data = post_checks(data)
    except Exception:
        pass

    logger.info('model_model=%s, model_value=%s, time=%s, memory_used=%s',
                node_type, 'post_checks', current_time_ms() - now, _memory_usage() - memory_usage)

    return data


def _run_model(data: dict, model: dict, all_models: list):
    model_id = get_required_model_param(model, 'model')
    model_value = model.get('value') or _list_except_item(all_models, model)

    now = current_time_ms()
    memory_usage = _memory_usage()

    module = _import_model(model_id.replace('-', '_'))
    # if no value is provided, use all the models but this one
    result = module.get('run')(model_value, data)

    logger.info('model_model=%s, model_value=%s, time=%s, memory_used=%s',
                model_id, model.get('value'), current_time_ms() - now, _memory_usage() - memory_usage)

    return {'data': data, 'model': model, 'version': module.get('version'), 'result': result}


def _run(data: dict, model: dict, all_models: list):
    return _run_model(data, model, all_models) if should_run(data, model) else None


def _run_serie(data: dict, models: list, stage: Union[int, List[int]] = None):
    return reduce(
        lambda prev, m: merge(
            prev, _run_parallel(prev, m, models) if isinstance(m, list) else [_run(_node_copy(prev), m, models)]
        ),
        _filter_models_stage(models, stage=stage),
        data
    )


def _run_parallel(data: dict, model: list, all_models: list):
    results = []

    max_workers = _max_workers(data.get('@type', data.get('type')))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_run, _node_copy(data), m, all_models) for m in model]

    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

    return results


def run(data: dict, models: list, stage: Union[int, List[int]] = None):
    # make sure we reset before recalculating the node
    reset_index()
    # run pre-checks if exist
    data = _run_pre_checks(data)
    data = _run_serie(data, models, stage=stage)
    # run post-checks if exist
    return _run_post_checks(data)
