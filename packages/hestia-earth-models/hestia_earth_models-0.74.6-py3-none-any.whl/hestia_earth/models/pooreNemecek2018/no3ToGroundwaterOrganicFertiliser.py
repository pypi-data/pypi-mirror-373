from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.utils.cycle import get_organic_fertiliser_N_total
from hestia_earth.models.utils.emission import _new_emission
from .no3ToGroundwaterSoilFlux_utils import _should_run, _get_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.units": ["kg", "kg N"],
                "term.termType": "organicFertiliser",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "organicFertiliser"}]
            }
        ],
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "clayContent"},
                {"@type": "Measurement", "value": "", "term.@id": "sandContent"},
                {"@type": "Measurement", "value": "", "term.@id": [
                    "precipitationAnnual", "precipitationLongTermAnnualMean"
                ]}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
TERM_ID = 'no3ToGroundwaterOrganicFertiliser'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, N_total: float, content_list_of_items: list):
    no3ToGroundwaterSoilFlux = _get_value(cycle, N_total, content_list_of_items, TERM_ID)
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    return [_emission(N_organic_fertiliser / N_total * no3ToGroundwaterSoilFlux if all([
        N_organic_fertiliser, N_total
    ]) else 0)]


def run(cycle: dict):
    should_run, N_total, content_list_of_items = _should_run(cycle, TERM_ID, TIER)
    return _run(cycle, N_total, content_list_of_items) if should_run else []
