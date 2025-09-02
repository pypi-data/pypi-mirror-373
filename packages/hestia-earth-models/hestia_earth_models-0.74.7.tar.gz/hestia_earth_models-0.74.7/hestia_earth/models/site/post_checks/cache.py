"""
Post Checks Cache

This model removes any cached data on the Site.
"""
from hestia_earth.models.utils import CACHE_KEY

REQUIREMENTS = {
    "Site": {}
}
RETURNS = {
    "Site": {}
}


def run(site: dict):
    if CACHE_KEY in site:
        del site[CACHE_KEY]
    return {**site}
