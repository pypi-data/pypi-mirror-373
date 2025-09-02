from hestia_earth.schema import NodeType
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logShouldRun
from hestia_earth.models.utils.product import find_by_product
from hestia_earth.models.utils.property import merge_properties
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": ""}],
        "transformations": [
            {
                "@type": "Transformation",
                "inputs": [{"@type": "Input"}],
                "none": {
                    "previousTransformationId": ""
                }
            }
        ]
    }
}
RETURNS = {
    "Transformation": [{
        "inputs": [{
            "@type": "Input"
        }]
    }]
}
MODEL_KEY = 'properties'
MODEL_LOG = '/'.join([MODEL, 'input', MODEL_KEY])


def _run_input(cycle: dict, input: dict):
    product = find_by_product(cycle, input)
    properties = (product or {}).get('properties', [])
    return {
        **input,
        'properties': merge_properties(input.get('properties', []), properties)
    } if len(properties) > 0 else input


def _run(cycle: dict, transformation: dict):
    inputs = transformation.get('inputs', [])
    return {
        **transformation,
        'inputs': [_run_input(cycle, input) for input in inputs]
    } if len(inputs) > 0 else transformation


def _first_transformations(cycle: dict):
    return [tr for tr in cycle.get('transformations', []) if not tr.get('previousTransformationId')]


def _should_run(cycle: dict):
    node_type = cycle.get('type', cycle.get('@type'))
    first_transformations = _first_transformations(cycle)
    has_first_transformations = len(first_transformations) > 0
    should_run = all([node_type == NodeType.CYCLE.value, has_first_transformations])
    logShouldRun(cycle, MODEL_LOG, None, should_run)
    return should_run


def run(cycle: dict):
    should_run = _should_run(cycle)
    transformations = _first_transformations(cycle) if should_run else []
    return non_empty_list([_run(cycle, tr) for tr in transformations])
