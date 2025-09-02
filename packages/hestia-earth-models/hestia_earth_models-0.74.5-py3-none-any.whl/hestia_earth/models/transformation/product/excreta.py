from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.tools import list_sum, non_empty_list
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import get_kg_term_units, _omit, sum_values
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.constant import Units, convert_to_N
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.input import total_excreta
from .. import MODEL

REQUIREMENTS = {
    "Transformation": {
        "term.termType": "excretaManagement",
        "inputs": [{"@type": "Input", "value": "", "term.termType": "excreta"}],
        "products": [{"@type": "Product", "value": ""}]
    }
}
RETURNS = {
    "Product": [{
        "term.termType": "excreta",
        "value": ""
    }]
}
LOOKUPS = {
    "emission": "causesExcretaMassLoss"
}
MODEL_KEY = 'excreta'
MODEL_LOG = '/'.join([MODEL, 'product', MODEL_KEY])

EMISSIONS_VALUE = {
    Units.KG_N.value: lambda input, emissions: sum_values([
        total_excreta([input]),
        -list_sum(list(map(convert_to_N, emissions)))
    ]),
    Units.KG.value: lambda input, emissions: total_excreta([input], Units.KG),
    Units.KG_VS.value: lambda input, emissions: total_excreta([input], Units.KG_VS)
}


def _find_by_units(values: list, units: str):
    return next((v for v in values if v.get('term', {}).get('units', '') == units), None)


def _find_excreta_product_id(transformation: dict, units: str):
    excreta_products = filter_list_term_type(transformation.get('products', []), TermTermType.EXCRETA)
    term_id = excreta_products[0].get('term', {}).get('@id') if len(excreta_products) > 0 else None
    return get_kg_term_units(term_id, units) if term_id else None


def _product_value(input: dict, emissions: list):
    units = input.get('term', {}).get('units')
    return EMISSIONS_VALUE.get(units, lambda *args: 0)(input, emissions)


def _add_product(transformation: dict, units: str, inputs: list, emissions: list):
    input_same_units = _find_by_units(inputs, units)
    # use the first extra product to build the id (in case another Product is used), else use Input id.
    term_id = _find_excreta_product_id(transformation, units) or input_same_units.get('term', {}).get('@id')
    value = list_sum(input_same_units.get('value', []), None)
    has_value = value is not None

    logRequirements(transformation, model=MODEL_LOG, term=term_id,
                    value=value,
                    has_value=has_value,
                    method='add')

    should_run = all([has_value])
    logShouldRun(transformation, MODEL_LOG, term_id, should_run)
    return {
        **_omit(input_same_units, ['fromCycle']),
        **_new_product(term_id, _product_value(input_same_units, emissions))
    } if should_run else None


def _can_update_product(product: dict, inputs: list):
    term_units = product.get('term', {}).get('units', '')
    return _find_by_units(inputs, term_units) is not None


def _update_product(transformation: dict, product: dict, inputs: list, emissions: list):
    term_id = product.get('term', {}).get('@id')
    term_units = product.get('term', {}).get('units', '')
    input_same_units = _find_by_units(inputs, term_units)
    value = _product_value(input_same_units, emissions)
    has_value = value is not None

    logRequirements(transformation, model=MODEL_LOG, term=term_id,
                    value=value,
                    has_value=has_value,
                    method='update')

    should_run = all([has_value])
    logShouldRun(transformation, MODEL_LOG, term_id, should_run)
    return {**product, 'value': [value]} if should_run else None


def _run(transformation: dict):
    emissions = transformation.get('emissions', [])
    # only some emissions will reduce the mass
    emissions = [e for e in emissions if get_lookup_value(e.get('term', {}), LOOKUPS['emission'])]

    inputs = filter_list_term_type(transformation.get('inputs', []), TermTermType.EXCRETA)
    products = filter_list_term_type(transformation.get('products', []), TermTermType.EXCRETA)
    missing_product_units = set([
        i.get('term', {}).get('units') for i in inputs if not _find_by_units(products, i.get('term', {}).get('units'))
    ])

    debugValues(transformation, model=MODEL_LOG,
                missing_product_units=';'.join(missing_product_units))

    return non_empty_list([
        #  update the Product value that already exist
        (
            _update_product(transformation, p, inputs, emissions) if _can_update_product(p, inputs) else p
        ) for p in products
    ]) + non_empty_list([
        #  add the Inputs as Product that do not exist
        _add_product(transformation, units, inputs, emissions) for units in missing_product_units
    ])


def _should_run(transformation: dict):
    node_type = transformation.get('type', transformation.get('@type'))
    should_run = all([
        node_type == SchemaType.TRANSFORMATION.value,
        transformation.get('term', {}).get('termType') == TermTermType.EXCRETAMANAGEMENT.value
    ])
    logShouldRun(transformation, MODEL_LOG, None, should_run)
    return should_run


def run(transformation: dict):
    return _run(transformation) if _should_run(transformation) else []
