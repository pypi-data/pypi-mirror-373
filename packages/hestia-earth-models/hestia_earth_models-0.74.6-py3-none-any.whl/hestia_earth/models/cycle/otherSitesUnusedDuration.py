from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.site import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "otherSites": [{
            "@type": "Site",
            "siteType": ["cropland", "glass and high accessible cover"]
        }],
        "otherSitesDuration": "",
        "practices": [{
            "@type": "Practice",
            "value": "> 0",
            "term.@id": "longFallowRatio",
            "site": {"@type": "Site"}
        }]
    }
}
RETURNS = {
    "The otherSitesUnusedDuration as an array of number": ""
}
MODEL_KEY = 'otherSitesUnusedDuration'
VALID_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
]
_PRACTICE_TERM_ID = 'longFallowRatio'


def _run(siteDuration: float, longFallowRatio: float):
    return siteDuration * (longFallowRatio - 1)


def _find_site_practice(practices: list, site_id: str):
    return list_sum(next(
        (p for p in practices if all([
            p.get('term', {}).get('@id') == _PRACTICE_TERM_ID,
            p.get('site') is None or p.get('site', {}).get('@id', p.get('site', {}).get('id')) == site_id
        ])),
        {}
    ).get('value'), None)


def _is_valid(data: dict): return all([
        data.get('valid-site'),
        data.get(_PRACTICE_TERM_ID) is not None,
        data.get('site-duration') is not None
    ])


def _should_run(cycle: dict):
    otherSitesDuration = cycle.get('otherSitesDuration', [])
    practices = cycle.get('practices', [])

    site_data = [
        {
            'site-id': site.get('@id', site.get('id')),
            'siteType': site.get('siteType'),
            'valid-site': valid_site_type(site, site_types=VALID_SITE_TYPES),
            'site-duration': otherSitesDuration[index] if len(otherSitesDuration) > index else None,
            _PRACTICE_TERM_ID: _find_site_practice(practices, site.get('@id'))
        }
        for index, site in enumerate(cycle.get('otherSites', []))
    ]

    has_valid_sites = any(map(_is_valid, site_data))

    logRequirements(cycle, model=MODEL, key=MODEL_KEY,
                    has_valid_sites=has_valid_sites,
                    site_data=log_as_table(site_data))

    should_run = all([has_valid_sites])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY)
    return should_run, site_data


def run(cycle: dict):
    should_run, site_data = _should_run(cycle)
    return [
        _run(data.get('site-duration'), data.get(_PRACTICE_TERM_ID)) if _is_valid(data) else None
        for data in site_data
    ] if should_run else []
