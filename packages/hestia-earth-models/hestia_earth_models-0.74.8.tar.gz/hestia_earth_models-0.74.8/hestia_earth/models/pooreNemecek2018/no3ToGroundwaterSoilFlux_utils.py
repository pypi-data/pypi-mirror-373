from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.cycle import (
    get_excreta_N_total, get_max_rooting_depth, get_crop_residue_decomposition_N_total,
    get_organic_fertiliser_N_total, get_inorganic_fertiliser_N_total
)
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.term import get_rice_paddy_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.excreta": "True",
        "completeness.cropResidue": "True",
        "completeness.fertiliser": "True",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": ["cropResidue", "excreta"],
            "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
        }],
        "inputs": [{
            "@type": "Input",
            "value": "",
            "term.units": ["kg", "kg N"],
            "term.termType": ["organicFertiliser", "inorganicFertiliser", "excreta"],
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            }
        }],
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
TERM_ID = 'no3ToGroundwaterSoilFlux'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _low_leaching_conditions(rooting_depth: float, clay: float, _s, precipitation: float, *args):
    return rooting_depth > 1.3 or clay > 50 or precipitation < 500


def _high_leaching_conditions(rooting_depth: float, _c, sand: float, precipitation: float, *args):
    return rooting_depth < 0.5 or sand > 85 or precipitation > 1300


def _flooded_rice_leaching_conditions(_rd, _c, _s, _r, product: dict):
    return product and product.get('term', {}).get('@id') in get_rice_paddy_terms()


def _other_leaching_conditions(*args):
    return True


NO3_LEACHING_FACTORS = {
    0.035: _flooded_rice_leaching_conditions,
    0.067: _low_leaching_conditions,
    0.23: _high_leaching_conditions,
    0.12: _other_leaching_conditions
}


def _should_run(cycle: dict, term=TERM_ID, tier=TIER):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    clay = most_relevant_measurement_value(measurements, 'clayContent', end_date)
    sand = most_relevant_measurement_value(measurements, 'sandContent', end_date)
    precipitation = most_relevant_measurement_value(
        measurements, 'precipitationAnnual', end_date
    ) or most_relevant_measurement_value(
        measurements, 'precipitationLongTermAnnualMean', end_date
    )
    rooting_depth = get_max_rooting_depth(cycle)
    primary_product = find_primary_product(cycle) or {}

    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    N_inorganic_fertiliser = get_inorganic_fertiliser_N_total(cycle)
    N_excreta = get_excreta_N_total(cycle)
    N_total = list_sum(non_empty_list([
        N_crop_residue,
        N_organic_fertiliser,
        N_inorganic_fertiliser,
        N_excreta
    ]))
    content_list_of_items = [rooting_depth, clay, sand, precipitation, primary_product]

    logRequirements(cycle, model=MODEL, term=term,
                    clayContent=clay,
                    sandContent=sand,
                    precipitation=precipitation,
                    rooting_depth=rooting_depth,
                    primary_product=primary_product.get('term', {}).get('@id'),
                    N_total=N_total,
                    N_crop_residue=N_crop_residue,
                    N_organic_fertiliser=N_organic_fertiliser,
                    N_inorganic_fertiliser=N_inorganic_fertiliser,
                    N_excreta=N_excreta)

    should_run = all([
        all(content_list_of_items),
        N_total >= 0
    ])
    logShouldRun(cycle, MODEL, term, should_run, methodTier=tier)
    return should_run, N_total, content_list_of_items


def get_leaching_factor(content_list_of_items: list):
    root_depth, clay, sand, precipitation, product = content_list_of_items
    # test conditions one by one and return the value associated for the first one that passes
    return next(
        (key for key, value in NO3_LEACHING_FACTORS.items() if value(root_depth, clay, sand, precipitation, product)),
        0.12  # default value for "Other"
    )


def _get_value(cycle: dict, N_total: float, content_list_of_items: list, term=TERM_ID):
    leaching_factor = get_leaching_factor(content_list_of_items)
    debugValues(cycle, model=MODEL, term=term,
                leaching_factor=leaching_factor)
    return N_total * leaching_factor * get_atomic_conversion(Units.KG_NO3, Units.TO_N)


def _run(cycle: dict, N_total: float, content_list_of_items: list):
    no3ToGroundwaterSoilFlux = _get_value(cycle, N_total, content_list_of_items)
    return [_emission(no3ToGroundwaterSoilFlux)]


def run(cycle: dict):
    should_run, N_total, content_list_of_items = _should_run(cycle)
    return _run(cycle, N_total, content_list_of_items) if should_run else []
