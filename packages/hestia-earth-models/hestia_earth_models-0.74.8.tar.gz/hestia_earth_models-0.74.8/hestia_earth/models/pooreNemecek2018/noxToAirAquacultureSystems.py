from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import total_excreta, total_excreta_tan
from hestia_earth.models.utils.aquacultureManagement import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "excreta",
            "term.units": "kg N",
            "properties": [
                {"@type": "Property", "value": "", "term.@id": "nitrogenContent"},
                {"@type": "Property", "value": "", "term.@id": "totalAmmoniacalNitrogenContentAsN"}
            ]
        }],
        "practices": [{"@type": "Practice", "value": "", "term.termType": "excretaManagement"}],
        "optional": {
            "site": {
                "@type": "Site",
                "siteType": ["pond", "sea or ocean"]
            }
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'noxToAirAquacultureSystems'
TIER = EmissionMethodTier.TIER_1.value
EF_Aqua = {'NH3N_NON': 0.0018, 'OtherN_NON': 0.0005}


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(excr_tan: float, excr_n: float):
    value = EF_Aqua['NH3N_NON'] * excr_tan + (EF_Aqua['OtherN_NON'] * (excr_n - excr_tan) if excr_n else 0)
    value = value * get_atomic_conversion(Units.KG_NOX, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    products = cycle.get('products', [])
    excr_n = total_excreta(products)
    excr_tan = total_excreta_tan(products)

    set_to_zero = not valid_site_type(cycle)  # if site is not water, set value to 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    excr_n=excr_n,
                    excr_tan=excr_tan,
                    set_to_zero=set_to_zero)

    should_run = any([excr_n or excr_tan or set_to_zero])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, excr_tan, excr_n, set_to_zero


def run(cycle: dict):
    should_run, excr_tan, excr_n, set_to_zero = _should_run(cycle)
    return [_emission(0)] if set_to_zero else _run(excr_tan, excr_n) if should_run else []
