from pkgutil import extend_path
from typing import Union, List
from hestia_earth.utils.tools import current_time_ms

from .log import logger
from .models import run as run_models

__path__ = extend_path(__path__, __name__)


def _required(message): raise Exception(message)


def run(data: dict, configuration: dict, stage: Union[int, List[int]] = None) -> dict:
    """
    Runs a set of models on a Node.

    Parameters
    ----------
    data : dict
        Either a `Cycle`, a `Site` or an `ImpactAssessment`.
    configuration : dict
        Configuration data which defines the order of the models to run.
    stage : int | list[int]
        For multi-stage calculations, will filter models by "stage". Can pass a single or multiple stage.

    Returns
    -------
    dict
        The data with updated content
    """
    now = current_time_ms()
    node_type = data.get('@type', data.get('type'))
    node_id = data.get('@id', data.get('id'))
    _required('Please provide an "@type" key in your data.') if node_type is None else None
    _required('Please provide a valid configuration.') if (configuration or {}).get('models') is None else None
    logger.info(f"Running models on {node_type}" + f" with id: {node_id}" if node_id else '')
    data = run_models(data, configuration.get('models', []), stage=stage)
    logger.info('time=%s, unit=ms', current_time_ms() - now)
    return data
