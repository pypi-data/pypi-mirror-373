from hestia_earth.models.utils.cache_sources import cache_sources

REQUIREMENTS = {
    "Site": {}
}
RETURNS = {
    "Site": {}
}


def run(site: dict): return cache_sources(site)
