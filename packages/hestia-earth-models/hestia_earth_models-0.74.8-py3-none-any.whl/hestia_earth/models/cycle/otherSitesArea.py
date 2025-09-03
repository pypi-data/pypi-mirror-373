from hestia_earth.schema import SiteSiteType

from .siteArea import _is_site_valid, _should_run as _should_run_site, _run

REQUIREMENTS = {
    "Cycle": {
        "otherSites": [{
            "@type": "Site",
            "siteType": "animal housing"
        }],
        "none": {
            "site": {
                "@type": "Site",
                "siteType": "animal housing"
            }
        },
        "animals": [{
            "@type": "Animal",
            "term.termType": "liveAnimal",
            "value": "> 0"
        }],
        "practices": [{
            "@type": "Practice",
            "term.@id": "stockingDensityAnimalHousingAverage"
        }]
    }
}
RETURNS = {
    "The otherSitesArea as an array of number": ""
}
MODEL_KEY = 'otherSitesArea'


def _should_run(cycle: dict):
    other_sites_valid = list(filter(
        lambda site: site.get('siteType') == SiteSiteType.ANIMAL_HOUSING.value,
        cycle.get('otherSites', [])
    ))

    should_run = all([
        not _is_site_valid(cycle.get('site', {})),
        len(other_sites_valid) == 1
    ]) and _should_run_site(cycle, other_sites_valid[0], key=MODEL_KEY)
    return should_run


def run(cycle: dict):
    other_sites = cycle.get('otherSites', [])
    other_sites_area = cycle.get('otherSitesArea')
    return [
        _run(cycle) if _is_site_valid(site) else other_sites_area[index] if other_sites_area else None
        for index, site in enumerate(other_sites)
    ] if _should_run(cycle) else []
