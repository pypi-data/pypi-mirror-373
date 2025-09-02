from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugValues
from hestia_earth.models.utils.input import get_total_irrigation_m3
from hestia_earth.models.utils.cycle import get_ecoClimateZone
from hestia_earth.models.utils.term import get_lookup_value, get_milkYield_terms
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
from . import MODEL

# From IPCC2019 Indirect N2O emission factor, in N [avg, min, max, std]
COEFF_NO3_N2O = [0.011, 0.00, 0.02, 0.005]
# Volatilized Nitrogen as NH3-N and NOx-N per kg N applied organic fertilisers and animal dung and urine
COEFF_N_NH3NOX_organic_animal = [0.21, 0.00, 0.31, 0.0775]
# Volatilized Nitrogen as NH3-N and NOx-N per kg N applied inorganic fertilisers
COEFF_N_NH3NOX_inorganic = [0.11, 0.02, 0.33, 0.0775]


def get_FracLEACH_H(cycle: dict, term_id: str):
    eco_climate_zone = get_ecoClimateZone(cycle)
    is_eco_climate_zone_dry = eco_climate_zone % 2 == 0
    irrigation_value_m3 = get_total_irrigation_m3(cycle)
    is_drip_irrigated = find_term_match(cycle.get('practices', []), 'irrigatedDripIrrigation', None) is not None

    debugValues(cycle, model=MODEL, term=term_id,
                is_eco_climate_zone_dry=is_eco_climate_zone_dry,
                irrigation_value_m3=irrigation_value_m3,
                is_drip_irrigated=is_drip_irrigated)

    return (0, 0, 0, 0) if all([
        is_eco_climate_zone_dry,
        any([irrigation_value_m3 <= 250, is_drip_irrigated])
    ]) else (0.24, 0.01, 0.73, 0.18)  # value, min, max, sd


# Indirect N2O emissions from volatilized NH3 and NOx
def get_FracNH3NOx_N2O(cycle: dict, term_id: str):
    eco_climate_zone = get_ecoClimateZone(cycle)
    is_eco_climate_zone_dry = eco_climate_zone % 2 == 0
    irrigation_value_m3 = get_total_irrigation_m3(cycle)
    is_drip_irrigated = find_term_match(cycle.get('practices', []), 'irrigatedDripIrrigation', None) is not None

    debugValues(cycle, model=MODEL, term=term_id,
                is_eco_climate_zone_dry=is_eco_climate_zone_dry,
                irrigation_value_m3=irrigation_value_m3,
                is_drip_irrigated=is_drip_irrigated)

    return (0.005, 0, 0.011, 0.00275) if all([
        is_eco_climate_zone_dry,
        any([irrigation_value_m3 <= 250, is_drip_irrigated])
    ]) else (0.014, 0.011, 0.017, 0.0015)  # value, min, max, sd


def get_yield_dm(term_id: str, term: dict):
    return safe_parse_float(
        get_lookup_value(term, 'IPCC_2019_Ratio_AGRes_YieldDM', model=MODEL, term=term_id), default=None
    )


def get_milkYield_practice(node: dict):
    terms = get_milkYield_terms()
    return next((p for p in node.get('practices', []) if p.get('term', {}).get('@id') in terms), {})


def check_consecutive(ints: list[int]) -> bool:
    """
    Checks whether a list of integers are consecutive.

    Used to determine whether annualised data is complete from every year from beggining to end.

    Parameters
    ----------
    ints : list[int]
        A list of integer values.

    Returns
    -------
    bool
        Whether or not the list of integers is consecutive.
    """
    range_list = list(range(min(ints), max(ints)+1)) if ints else []
    return all(a == b for a, b in zip(ints, range_list))


N2O_FACTORS = {
    # All N inputs in dry climate
    'dry': {
        'value': 0.005,
        'min': 0,
        'max': 0.011
    },
    'wet': {
        # Synthetic fertiliser inputs in wet climate
        TermTermType.INORGANICFERTILISER: {
            'value': 0.016,
            'min': 0.013,
            'max': 0.019
        },
        # Other N inputs in wet climate
        TermTermType.ORGANICFERTILISER: {
            'value': 0.006,
            'min': 0.001,
            'max': 0.011
        },
        TermTermType.CROPRESIDUE: {
            'value': 0.006,
            'min': 0.001,
            'max': 0.011
        }
    },
    'default': {
        'value': 0.01,
        'min': 0.001,
        'max': 0.018
    },
    'flooded_rice': {
        'value': 0.004,
        'min': 0,
        'max': 0.029
    }
}


def _get_waterRegime_lookup(model_term_id: str, practice: dict, col: str):
    return safe_parse_float(
        get_lookup_value(practice.get('term', {}), col, model=MODEL, term=model_term_id), default=None
    )


def _is_wet(ecoClimateZone: str = None):
    return get_ecoClimateZone_lookup_value(ecoClimateZone, 'wet') == 1 if ecoClimateZone else None


def ecoClimate_factors(factors: dict, input_term_type: TermTermType = None, ecoClimateZone: str = None):
    is_wet = _is_wet(ecoClimateZone)
    factors_key = 'default' if is_wet is None else 'wet' if is_wet else 'dry'
    return (factors[factors_key].get(input_term_type, factors[factors_key]), ecoClimateZone is None)


def _flooded_rice_factors(model_term_id: str, cycle: dict):
    lookup_name = 'IPCC_2019_N2O_rice'
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.WATERREGIME)
    practice = next((p for p in practices if _get_waterRegime_lookup(model_term_id, p, lookup_name) is not None), None)

    factors = {
        'value': _get_waterRegime_lookup(model_term_id, practice, lookup_name),
        'min': _get_waterRegime_lookup(model_term_id, practice, lookup_name + '-min'),
        'max': _get_waterRegime_lookup(model_term_id, practice, lookup_name + '-max')
    } if practice else N2O_FACTORS['flooded_rice']

    return (factors, practice is None)


def get_N2O_factors(
    model_term_id: str,
    cycle: dict,
    input_term_type: TermTermType,
    ecoClimateZone: str = None,
    flooded_rice: bool = False
):
    return _flooded_rice_factors(model_term_id, cycle) if flooded_rice \
        else ecoClimate_factors(N2O_FACTORS, input_term_type, ecoClimateZone)
