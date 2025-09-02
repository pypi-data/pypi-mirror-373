from os.path import dirname, abspath
import sys

from hestia_earth.models.utils import _run_in_serie
from . import cache_years, cache_geospatialDatabase, cache_sources, country

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)

MODELS = [
    cache_years.run,
    cache_geospatialDatabase.run,
    cache_sources.run,
    country.run
]


def run(data: dict): return _run_in_serie(data, MODELS)
