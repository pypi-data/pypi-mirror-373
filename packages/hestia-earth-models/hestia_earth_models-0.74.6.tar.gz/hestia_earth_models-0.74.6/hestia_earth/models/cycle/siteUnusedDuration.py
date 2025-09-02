from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.site import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "siteType": ["cropland", "glass and high accessible cover"]
        },
        "siteDuration": "> 0",
        "practices": [{"@type": "Practice", "value": "> 0", "term.@id": "longFallowRatio"}]
    }
}
RETURNS = {
    "The siteUnusedDuration as a number": ""
}
MODEL_KEY = 'siteUnusedDuration'
VALID_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
]


def _run(cycle: dict, longFallowRatio: float):
    siteDuration = cycle.get('siteDuration')
    return siteDuration * (longFallowRatio - 1)


def _should_run(cycle: dict):
    site_id = cycle.get('site', {}).get('@id', cycle.get('site', {}).get('id'))
    site_type_valid = valid_site_type(cycle.get('site'), site_types=VALID_SITE_TYPES)

    siteDuration = cycle.get('siteDuration', 0)

    practices = cycle.get('practices', [])
    longFallowRatio = list_sum(next((
        p for p in practices if all([
            p.get('term', {}).get('@id') == 'longFallowRatio',
            p.get('site') is None or p.get('site', {}).get('@id', p.get('site', {}).get('id')) == site_id
        ])
    ), {}).get('value'), None)

    logRequirements(cycle, model=MODEL, key=MODEL_KEY,
                    site_type_valid=site_type_valid,
                    siteDuration=siteDuration,
                    longFallowRatio=longFallowRatio)

    should_run = all([site_type_valid, siteDuration > 0, longFallowRatio is not None])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY)
    return should_run, longFallowRatio


def run(cycle: dict):
    should_run, longFallowRatio = _should_run(cycle)
    return _run(cycle, longFallowRatio) if should_run else None
