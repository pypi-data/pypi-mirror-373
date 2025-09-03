from hestia_earth.models.utils import CACHE_KEY

REQUIREMENTS = {
    "Cycle": {}
}
RETURNS = {
    "Cycle": {}
}


def run(cycle: dict):
    if CACHE_KEY in cycle:
        del cycle[CACHE_KEY]
    return {**cycle}
