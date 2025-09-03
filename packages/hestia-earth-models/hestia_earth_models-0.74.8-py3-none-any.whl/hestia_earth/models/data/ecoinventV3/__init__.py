import os

from hestia_earth.models.log import logger

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ENV_FOLDER = 'ECOINVENT_V3_FOLDER'
_DATA_FOLDER = os.getenv(_ENV_FOLDER) or _CURRENT_DIR
_ECOINVENT_VERSION = os.getenv('ECOINVENT_VERSION', '3.9')


def get_filepath(term_type: str):
    filename = f"ecoinventV{_ECOINVENT_VERSION.replace('.', '_')}-{term_type}.csv"
    filepath = os.path.join(_DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        logger.warning('%s file not found. Please make sure to set env variable "%s".', filename, _ENV_FOLDER)
        return None

    return filepath
