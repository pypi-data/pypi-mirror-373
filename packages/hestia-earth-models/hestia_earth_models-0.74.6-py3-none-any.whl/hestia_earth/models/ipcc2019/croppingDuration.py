from hestia_earth.schema import PracticeStatsDefinition
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.product import has_flooded_rice
from hestia_earth.models.utils.lookup import get_region_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "cycleDuration": "",
        "products": [{
            "@type": "Product",
            "primary": "True",
            "value": "",
            "term.@id": ["riceGrainInHuskFlooded", "ricePlantFlooded"],
            "term.termType": "crop"
        }],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        }
    }
}
LOOKUPS = {
    "region-ch4ef-IPCC2019": [
        "Rice_croppingDuration_days", "Rice_croppingDuration_days_min", "Rice_croppingDuration_days_max",
        "Rice_croppingDuration_days_sd"
    ]
}
RETURNS = {
    "Practice": [{
        "value": "",
        "min": "",
        "max": "",
        "sd": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'croppingDuration'
LOOKUP_TABLE = 'region-ch4ef-IPCC2019.csv'
LOOKUP_COL_PREFIX = 'Rice_croppingDuration_days'


def _practice(value: float, min: float, max: float, sd: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    practice['min'] = [min]
    practice['max'] = [max]
    practice['sd'] = [sd]
    practice['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return practice


def _get_value(country: str, col: str):
    return safe_parse_float(
        get_region_lookup_value(LOOKUP_TABLE, country, col, model=MODEL, term=TERM_ID), default=None
    )


def _run(country: str):
    value = _get_value(country, LOOKUP_COL_PREFIX)
    min = _get_value(country, f"{LOOKUP_COL_PREFIX}_min")
    max = _get_value(country, f"{LOOKUP_COL_PREFIX}_max")
    sd = _get_value(country, f"{LOOKUP_COL_PREFIX}_sd")
    return [_practice(value, min, max, sd)]


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {}).get('@id')
    croppingDuration = _get_value(country, LOOKUP_COL_PREFIX) or 0

    cycleDuration = cycle.get('cycleDuration', 0)
    flooded_rice = has_flooded_rice(cycle.get('products', []))

    croppingDuration_below_cycleDuration = croppingDuration <= cycleDuration

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    country=country,
                    has_flooded_rice=flooded_rice,
                    cycleDuration=cycle.get('cycleDuration'),
                    croppingDuration=croppingDuration,
                    croppingDuration_below_cycleDuration=croppingDuration_below_cycleDuration)

    should_run = all([country, cycleDuration > 0, croppingDuration_below_cycleDuration, flooded_rice])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, country


def run(cycle: dict):
    should_run, country = _should_run(cycle)
    return _run(country) if should_run else []
