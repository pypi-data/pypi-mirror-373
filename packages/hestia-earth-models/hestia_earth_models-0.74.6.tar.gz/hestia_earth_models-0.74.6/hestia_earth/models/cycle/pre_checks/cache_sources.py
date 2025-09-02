from hestia_earth.models.utils.cache_sources import cache_sources

REQUIREMENTS = {
    "Cycle": {}
}
RETURNS = {
    "Cycle": {}
}


def run(cycle: dict): return cache_sources(cycle)
