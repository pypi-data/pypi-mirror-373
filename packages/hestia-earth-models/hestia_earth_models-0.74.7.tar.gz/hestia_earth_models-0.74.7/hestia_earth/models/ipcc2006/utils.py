from hestia_earth.utils.model import find_primary_product

COEFF_NH3NOX_N2O = 0.01
COEFF_NO3_N2O = 0.0075
N2O_FACTORS = {
    'default': {
        'value': 0.01,
        'min': 0.003,
        'max': 0.03
    },
    'flooded_rice': {
        'value': 0.003,
        'min': 0,
        'max': 0.006
    }
}


def get_N_N2O_excreta_coeff_from_primary_product(cycle: dict):
    product = find_primary_product(cycle)
    term = product.get('term', {}) if product else {}
    # TODO: should use the coefficient from lookup table
    # percent = get_lookup_value(lookup, term, col)
    # return safe_parse_float(percent, 0.02)
    has_sheep_goat_products = term.get('@id') in ['sheep', 'goat']
    return 0.01 if has_sheep_goat_products else 0.02
