from os.path import dirname, abspath
import sys

from hestia_earth.models.utils import _run_in_serie
from . import cycle, site, remove_cache_fields

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)

MODELS = [
    cycle.run,
    site.run,
    remove_cache_fields.run
]


def run(data: dict): return _run_in_serie(data, MODELS)
