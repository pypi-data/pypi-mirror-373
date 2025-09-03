from hestia_earth.models.log import debugValues
from hestia_earth.models.utils import CACHE_KEY, cached_value
from hestia_earth.models.utils.site import CACHE_YEARS_KEY, related_years

REQUIREMENTS = {
    "Site": {}
}
RETURNS = {
    "Site": {}
}


def _should_run(site: dict):
    years = related_years(site)
    has_cache = cached_value(site, CACHE_YEARS_KEY) is not None

    debugValues(site,
                years=';'.join([str(y) for y in years]),
                has_cache=has_cache)

    should_run = all([
        not has_cache,
        len(years) > 0
    ])
    return should_run, years


def run(site: dict):
    should_run, years = _should_run(site)
    return {
        **site,
        CACHE_KEY: cached_value(site) | {CACHE_YEARS_KEY: years}
    } if should_run else site
