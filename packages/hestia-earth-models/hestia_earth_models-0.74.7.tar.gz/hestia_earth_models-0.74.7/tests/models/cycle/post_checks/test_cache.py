from hestia_earth.models.utils import CACHE_KEY

from hestia_earth.models.cycle.post_checks.cache import run


def rest_run():
    cycle = {CACHE_KEY: {}}
    assert CACHE_KEY not in run(cycle)
