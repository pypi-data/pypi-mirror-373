from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_inorganic_fertiliser_P_total
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from . import MODEL
from .utils import get_liquid_slurry_sludge_P_total

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.termType": "organicFertiliser"
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
            "country": {"@type": "Term", "termType": "region"},
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "slope"}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "organicFertiliser": "OrganicFertiliserClassification"
}
TERM_ID = 'pToSurfaceWaterSoilFlux'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, slope: list, excreta_p_total: float):
    lss_P, other_organic_P = get_liquid_slurry_sludge_P_total(cycle)
    inorganic_P = get_inorganic_fertiliser_P_total(cycle)
    value_slope = 0 if slope < 3 else 1

    debugValues(cycle, model=MODEL, term=TERM_ID,
                value_slope=value_slope,
                inorganic_P=inorganic_P,
                liquid_slurry_sludge_P=lss_P,
                other_organic_P=other_organic_P)

    value = value_slope * (1 + ((inorganic_P or 0) * 0.2 + lss_P * 0.7 + (other_organic_P + excreta_p_total) * 0.4)/80)
    return [_emission(value)]


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    slope = most_relevant_measurement_value(measurements, 'slope', end_date)
    # TODO: add excreta as input when is gone onto pasture
    excreta_p_total = 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    slope=slope,
                    excreta_p_total=excreta_p_total)

    should_run = all([slope is not None, excreta_p_total >= 0])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, slope, excreta_p_total


def run(cycle: dict):
    should_run, slope, excreta_p_total = _should_run(cycle)
    return _run(cycle, slope, excreta_p_total) if should_run else []
