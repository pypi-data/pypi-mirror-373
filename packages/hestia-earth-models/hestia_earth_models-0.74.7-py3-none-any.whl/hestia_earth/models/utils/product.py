from hestia_earth.schema import SchemaType, TermTermType, UNIQUENESS_FIELDS
from hestia_earth.utils.model import filter_list_term_type, find_term_match, linked_node
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list, get_dict_key

from .blank_node import get_total_value, get_total_value_converted
from .constant import Units
from .currency import DEFAULT_CURRENCY
from .property import _get_nitrogen_content, get_node_property_value
from .term import get_rice_paddy_terms, download_term
from .method import include_model


def _new_product(term, value: float = None, model=None):
    node = {'@type': SchemaType.PRODUCT.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(term))
    if value is not None:
        node['value'] = [value]
    elif value == 0:
        node['economicValueShare'] = 0
        node['revenue'] = 0
        node['currency'] = DEFAULT_CURRENCY
    return include_model(node, model)


def _match_list_el(source: list, dest: list, key: str):
    src_values = non_empty_list([get_dict_key(x, key) for x in source])
    dest_values = non_empty_list([get_dict_key(x, key) for x in dest])
    return sorted(src_values) == sorted(dest_values)


def _match_el(source: dict, dest: dict, fields: list):
    def match(key: str):
        keys = key.split('.')
        is_list = len(keys) >= 2 and (
            isinstance(get_dict_key(source, keys[0]), list) or
            isinstance(get_dict_key(dest, keys[0]), list)
        )
        return _match_list_el(
            get_dict_key(source, keys[0]) or [],
            get_dict_key(dest, keys[0]) or [],
            '.'.join(keys[1:])
        ) if is_list else (get_dict_key(dest, key) is None or get_dict_key(source, key) == get_dict_key(dest, key))

    return all(map(match, fields))


def find_by_product(node: dict, product: dict, list_key: str = 'products'):
    keys = UNIQUENESS_FIELDS.get(node.get('type', node.get('@type')), {}).get(list_key, ['term.@id'])
    products = node.get(list_key, [])
    return next((p for p in products if _match_el(p, product, keys)), None)


def has_flooded_rice(products: list):
    """
    Checks if one of the product is a flooded rice.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        True if one product matches a rice paddy crop.
    """
    terms = get_rice_paddy_terms()
    return any([True for p in products if p.get('term', {}).get('@id') in terms])


def abg_total_residue_nitrogen_content(products: list):
    """
    Get the nitrogen content from the `aboveGroundCropResidueTotal` product.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    return _get_nitrogen_content(find_term_match(products, 'aboveGroundCropResidueTotal'))


def abg_residue_on_field_nitrogen_content(products: list):
    """
    Get the total nitrogen content from the above ground `cropResidue` left on the field.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    left_on_field = find_term_match(products, 'aboveGroundCropResidueLeftOnField').get('value', [0])
    incorporated = find_term_match(products, 'aboveGroundCropResidueIncorporated').get('value', [0])
    return list_sum(left_on_field + incorporated) * abg_total_residue_nitrogen_content(products) / 100


def discarded_total_residue_nitrogen_content(products: list):
    """
    Get the nitrogen content from the `discardedCropTotal` product.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    return _get_nitrogen_content(find_term_match(products, 'discardedCropTotal'))


def discarded_residue_on_field_nitrogen_content(products: list):
    """
    Get the total nitrogen content from the discarded `cropResidue` left on the field.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    left_on_field = find_term_match(products, 'discardedCropLeftOnField').get('value', [0])
    incorporated = find_term_match(products, 'discardedCropIncorporated').get('value', [0])
    return list_sum(left_on_field + incorporated) * discarded_total_residue_nitrogen_content(products) / 100


def get_animal_produced_nitrogen(model: str, products: list) -> float:
    # TODO: refactor this to use `convert_to_nitrogen`
    products = filter_list_term_type(products, [
        TermTermType.LIVEANIMAL, TermTermType.ANIMALPRODUCT, TermTermType.LIVEAQUATICSPECIES
    ])

    def prop_value(input: dict):
        value = get_node_property_value(model, input, 'nitrogenContent')
        return value or get_node_property_value(model, input, 'crudeProteinContent', default=0) / 6.25

    def product_value(product: dict):
        value = convert_product_to_unit(product, Units.KG_LIVEWEIGHT)
        property = prop_value(product)
        return value * property if all([value, property]) else 0

    return list_sum(list(map(product_value, products)))


PRODUCT_UNITS_CONVERSIONS = {
    Units.KG.value: {
        Units.KG_LIVEWEIGHT.value: [],
        Units.KG_N.value: [
            ('nitrogenContent', True)
        ],
        Units.KG_VS.value: [
            ('volatileSolidsContent', True)
        ],
        Units.KG_P.value: [
            ('phosphorusContentAsP', True)
        ],
        Units.KG_P2O5.value: [
            ('phosphateContentAsP2O5', True)
        ]
    },
    Units.KG_N.value: {
        Units.KG.value: [
            ('nitrogenContent', False)
        ],
        Units.KG_VS.value: [
            ('nitrogenContent', False),
            ('volatileSolidsContent', True)
        ],
        Units.KG_P.value: [
            ('nitrogenContent', False),
            ('phosphorusContentAsP', True)
        ],
        Units.KG_P2O5.value: [
            ('nitrogenContent', False),
            ('phosphateContentAsP2O5', True)
        ]
    },
    Units.KG_VS.value: {
        Units.KG.value: [
            ('volatileSolidsContent', False)
        ],
        Units.KG_N.value: [
            ('volatileSolidsContent', False),
            ('nitrogenContent', True)
        ]
    },
    Units.KG_LIVEWEIGHT.value: {
        Units.NUMBER.value: [
            ('liveweightPerHead', True)
        ],
        Units.HEAD.value: [
            ('liveweightPerHead', True)
        ],
        Units.KG_LIVEWEIGHT.value: [],
        Units.KG_COLD_CARCASS_WEIGHT.value: [
            ('processingConversionLiveweightToColdCarcassWeight', True)
        ],
        Units.KG_COLD_DRESSED_CARCASS_WEIGHT.value: [
            ('processingConversionLiveweightToColdDressedCarcassWeight', True)
        ],
        Units.KG_READY_TO_COOK_WEIGHT.value: [
            (
                [
                    'processingConversionLiveweightToColdCarcassWeight',
                    'processingConversionColdCarcassWeightToReadyToCookWeight'
                ],
                True
            ),
            (
                [
                    'processingConversionLiveweightToColdDressedCarcassWeight',
                    'processingConversionColdDressedCarcassWeightToReadyToCookWeight'
                ],
                True
            )
        ],
        Units.KG_P.value: [
            ('phosphorusContentAsP', True)
        ],
        Units.KG_P2O5.value: [
            ('phosphateContentAsP2O5', True)
        ]
    },
    Units.KG_COLD_CARCASS_WEIGHT.value: {
        Units.KG_LIVEWEIGHT.value: [
            ('processingConversionLiveweightToColdCarcassWeight', False)
        ],
        Units.KG_COLD_DRESSED_CARCASS_WEIGHT.value: [],
        Units.KG_COLD_CARCASS_WEIGHT.value: [],
        Units.KG_READY_TO_COOK_WEIGHT.value: [
            ('processingConversionColdCarcassWeightToReadyToCookWeight', True)
        ],
        Units.KG_P.value: [
            ('phosphorusContentAsP', True)
        ],
        Units.KG_P2O5.value: [
            ('phosphateContentAsP2O5', True)
        ]
    },
    Units.KG_COLD_DRESSED_CARCASS_WEIGHT.value: {
        Units.KG_LIVEWEIGHT.value: [
            ('processingConversionLiveweightToColdDressedCarcassWeight', False),
            # fallback when cold dressed carcass weight is not provided
            ('processingConversionLiveweightToColdCarcassWeight', False)
        ],
        Units.KG_COLD_DRESSED_CARCASS_WEIGHT.value: [],
        Units.KG_COLD_CARCASS_WEIGHT.value: [],
        Units.KG_READY_TO_COOK_WEIGHT.value: [
            ('processingConversionColdDressedCarcassWeightToReadyToCookWeight', True)
        ],
        Units.KG_P.value: [
            ('phosphorusContentAsP', True)
        ],
        Units.KG_P2O5.value: [
            ('phosphateContentAsP2O5', True)
        ]
    },
    Units.KG_READY_TO_COOK_WEIGHT.value: {
        Units.KG_LIVEWEIGHT.value: [
            (
                [
                    'processingConversionColdCarcassWeightToReadyToCookWeight',
                    'processingConversionLiveweightToColdCarcassWeight',
                ],
                False
            ),
            (
                [
                    'processingConversionColdDressedCarcassWeightToReadyToCookWeight',
                    'processingConversionLiveweightToColdDressedCarcassWeight'
                ],
                False
            )
        ],
        Units.KG_COLD_CARCASS_WEIGHT.value: [
            ('processingConversionColdCarcassWeightToReadyToCookWeight', False)
        ],
        Units.KG_COLD_DRESSED_CARCASS_WEIGHT.value: [
            ('processingConversionColdDressedCarcassWeightToReadyToCookWeight', False)
        ],
        Units.KG_READY_TO_COOK_WEIGHT.value: [],
        Units.KG_P.value: [
            ('phosphorusContentAsP', True)
        ],
        Units.KG_P2O5.value: [
            ('phosphateContentAsP2O5', True)
        ]
    },
    Units.HEAD.value: {
        Units.KG_LIVEWEIGHT.value: [
            ('liveweightPerHead', True)
        ]
    },
    Units.NUMBER.value: {
        Units.KG_LIVEWEIGHT.value: [
            ('liveweightPerHead', True)
        ],
        Units.KG_COLD_CARCASS_WEIGHT.value: [
            ('liveweightPerHead', True),
            ('processingConversionLiveweightToColdCarcassWeight', True)
        ]
    }
}


def convert_product_to_unit(product: dict, dest_unit: Units):
    from_units = product.get('term', {}).get('units')
    to_units = dest_unit if isinstance(dest_unit, str) else dest_unit.value
    conversions = PRODUCT_UNITS_CONVERSIONS.get(from_units, {}).get(to_units)
    return None if len(product.get('value', [])) == 0 else 0 if conversions is None else list_sum(
        flatten([
            get_total_value_converted([product], properties, multiply) for properties, multiply in conversions
        ]) if len(conversions) > 0 else get_total_value([product])
    )


def liveweight_produced(products: list):
    return list_sum([convert_product_to_unit(p, Units.KG_LIVEWEIGHT) for p in products])
