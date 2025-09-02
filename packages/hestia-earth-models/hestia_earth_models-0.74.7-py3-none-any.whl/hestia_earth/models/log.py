import os
import sys
import logging
from typing import Union, List

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
_EXTENDED_LOGS = os.getenv('LOG_EXTENDED', 'true') == 'true'
_LOG_DATE_FORMAT = os.getenv('LOG_DATE_FORMAT', '%Y-%m-%dT%H:%M:%S%z')

# disable root logger
root_logger = logging.getLogger()
root_logger.disabled = True

# create custom logger
logger = logging.getLogger('hestia_earth.models')
logger.removeHandler(sys.stdout)
logger.setLevel(logging.getLevelName(LOG_LEVEL))


def log_to_file(filepath: str):
    """
    By default, all logs are saved into a file with path stored in the env variable `LOG_FILENAME`.
    If you do not set the environment variable `LOG_FILENAME`, you can use this function with the file path.

    Parameters
    ----------
    filepath : str
        Path of the file.
    """
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        _LOG_DATE_FORMAT
    ) if _EXTENDED_LOGS else logging.Formatter(
        '{"logger": "%(name)s", "message": "%(message)s"}',
        _LOG_DATE_FORMAT
    )
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setFormatter(formatter)
    handler.setLevel(logging.getLevelName(LOG_LEVEL))
    logger.addHandler(handler)


LOG_FILENAME = os.getenv('LOG_FILENAME')
if LOG_FILENAME is not None:
    log_to_file(LOG_FILENAME)


def _join_args(**kwargs): return ', '.join([f"{key}={value}" for key, value in kwargs.items()])


def _log_node_suffix(node: dict):
    node_type = node.get('@type', node.get('type'))
    node_id = node.get('@id', node.get('id', node.get('term', {}).get('@id')))
    return f"{node_type.lower()}={node_id}, " if node_type else ''


def debugValues(log_node: dict, **kwargs):
    logger.debug(_log_node_suffix(log_node) + _join_args(**kwargs))


def logRequirements(log_node: dict, **kwargs):
    logger.info(_log_node_suffix(log_node) + 'requirements=true, ' + _join_args(**kwargs))


def logShouldRun(log_node: dict, model: str, term: Union[str, None], should_run: bool, **kwargs):
    extra = (', ' + _join_args(**kwargs)) if len(kwargs.keys()) > 0 else ''
    logger.info(_log_node_suffix(log_node) + 'should_run=%s, model=%s, term=%s' + extra, should_run, model, term)


def debugMissingLookup(lookup_name: str, row: str, row_value: str, col: str, value, **kwargs):
    if value is None or value == '':
        extra = (', ' + _join_args(**kwargs)) if len(kwargs.keys()) > 0 else ''
        logger.warning(f'Missing lookup={lookup_name}, {row}={row_value}, column={col}' + extra)


def logErrorRun(model: str, term: str, error: str):
    logger.error('model=%s, term=%s, error=%s', model, term, error)


def log_as_table(values: Union[list, dict], ignore_keys: list = []):
    """
    Log a list of values to display as a table.
    Can either use a single dictionary, represented using id/value pair,
    or a list of dictionaries using their keys as columns.

    Parameters
    ----------
    values : list | dict
        Values to display as a table.
    """
    return ';'.join([
        f"id:{k}_value:{v}" for k, v in values.items() if k not in ignore_keys
    ] if isinstance(values, dict) else [
        (
            '_'.join([f"{k}:{v}" for k, v in value.items() if k not in ignore_keys])
            if isinstance(value, dict) else str(value)
        ) for value in values
    ]) or 'None'


def log_blank_nodes_id(blank_nodes: List[dict]):
    """
    Log a list of blank node ids to display as a table.

    Parameters
    ----------
    values : list
        List of blank nodes, like Product, Input, Measurement, etc.
    """
    return ';'.join([p.get('term', {}).get('@id') for p in blank_nodes if p.get('term', {}).get('@id')]) or 'None'
