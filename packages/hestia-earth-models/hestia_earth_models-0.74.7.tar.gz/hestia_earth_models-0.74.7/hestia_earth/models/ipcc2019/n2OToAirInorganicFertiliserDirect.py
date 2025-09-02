from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_ecoClimateZone, get_inorganic_fertiliser_N_total
from hestia_earth.models.utils.product import has_flooded_rice
from .utils import get_N2O_factors
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.units": ["kg", "kg N"],
                "term.termType": "inorganicFertiliser",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "inorganicFertiliser"}]
            }
        ],
        "optional": {
            "endDate": "",
            "site": {
                "@type": "Site",
                "measurements": [
                    {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
                ]
            },
            "products": [{"@type": "Product", "term.@id": "riceGrainInHuskFlooded"}],
            "practices": [{"@type": "Practice", "term.termType": "waterRegime"}]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "min": "",
        "max": "",
        "sd": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled",
        "methodModelDescription": ["Aggregated version", "Disaggregated version"]
    }]
}
LOOKUPS = {
    "waterRegime": ["IPCC_2019_N2O_rice", "IPCC_2019_N2O_rice-min", "IPCC_2019_N2O_rice-max"]
}
TERM_ID = 'n2OToAirInorganicFertiliserDirect'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, min: float, max: float, sd: float, aggregated: bool = False):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['sd'] = [sd]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['methodModelDescription'] = 'Aggregated version' if aggregated else 'Disaggregated version'
    return emission


def _run(cycle: dict, N_total: float, ecoClimateZone: str = None, flooded_rice: bool = False):
    converted_N_total = N_total * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    factors, aggregated = get_N2O_factors(
        TERM_ID, cycle, TermTermType.INORGANICFERTILISER, ecoClimateZone=ecoClimateZone, flooded_rice=flooded_rice
    )

    debugValues(cycle, model=MODEL, term=TERM_ID,
                factors_used=log_as_table(factors),
                aggregated=aggregated)

    value = converted_N_total * factors['value']
    min = converted_N_total * factors['min']
    max = converted_N_total * factors['max']
    sd = converted_N_total * (factors['max'] - factors['min'])/4
    return [_emission(value, min, max, sd, aggregated=aggregated)]


def _should_run(cycle: dict):
    term_type_complete = _is_term_type_complete(cycle, 'fertiliser')
    N_total = get_inorganic_fertiliser_N_total(cycle)
    ecoClimateZone = get_ecoClimateZone(cycle)

    flooded_rice = has_flooded_rice(cycle.get('products', []))

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_fertiliser_complete=term_type_complete,
                    N_total=N_total,
                    has_flooded_rice=flooded_rice,
                    ecoClimateZone=ecoClimateZone)

    should_run = all([N_total is not None, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, N_total, ecoClimateZone, flooded_rice


def run(cycle: dict):
    should_run, N_total, ecoClimateZone, flooded_rice = _should_run(cycle)
    return _run(cycle, N_total, ecoClimateZone, flooded_rice) if should_run else []
