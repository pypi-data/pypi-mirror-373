from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logRequirements
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.lookup import get_region_lookup_value
from . import MODEL
from .utils import _should_run, _practice

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        }
    }
}
LOOKUPS = {
    "crop": "cropGroupingResidue",
    "region-crop-cropGroupingResidue-removed": ""
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'residueRemoved'
LOOKUP_NAME = 'region-crop-cropGroupingResidue-removed.csv'


def _get_default_percent(cycle: dict, term: dict, country_id: str):
    crop_grouping = get_lookup_value(term, LOOKUPS['crop'], model=MODEL, term=TERM_ID)
    percent = get_region_lookup_value(
        LOOKUP_NAME, country_id, crop_grouping, model=MODEL, term=TERM_ID
    ) if crop_grouping else None
    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    crop_grouping=crop_grouping,
                    country_id=country_id,
                    percent=percent)
    return safe_parse_float(percent, default=None)


def _run(cycle: dict, remaining_value: float, primary_product: dict, country_id: str):
    term = primary_product.get('term', {})
    value = _get_default_percent(cycle, term, country_id)
    return [] if value is None else [_practice(TERM_ID, min(round(value * 100, 7), remaining_value))]


def run(cycle: dict):
    should_run, remaining_value, primary_product, country_id = _should_run(TERM_ID, cycle, require_country=True)
    return _run(cycle, remaining_value, primary_product, country_id) if should_run else []
