import os
import sys
import logging

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
_EXTENDED_LOGS = os.getenv('LOG_EXTENDED', 'true') == 'true'
_LOG_DATE_FORMAT = os.getenv('LOG_DATE_FORMAT', '%Y-%m-%dT%H:%M:%S%z')

# disable root logger
root_logger = logging.getLogger()
root_logger.disabled = True

# create custom logger
logger = logging.getLogger('hestia_earth.orchestrator')
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


def _log_node_suffix(node: dict = {}):
    node_type = node.get('@type', node.get('type')) if node else None
    node_id = node.get('@id', node.get('id', node.get('term', {}).get('@id'))) if node else None
    return f"{node_type.lower()}={node_id}, " if node_type else ''


def debugValues(log_node: dict, **kwargs):
    logger.debug(_log_node_suffix(log_node) + _join_args(**kwargs))


def logShouldRun(log_node: dict, model: str, term: str, should_run: bool, **kwargs):
    extra = (', ' + _join_args(**kwargs)) if len(kwargs.keys()) > 0 else ''
    logger.info(_log_node_suffix(log_node) + 'should_run=%s, model=%s, term=%s' + extra, should_run, model, term)


def logShouldMerge(log_node: dict, model: str, term: str, should_merge: bool, **kwargs):
    extra = (', ' + _join_args(**kwargs)) if len(kwargs.keys()) > 0 else ''
    logger.info(_log_node_suffix(log_node) + 'should_merge=%s, model=%s, term=%s' + extra, should_merge, model, term)
