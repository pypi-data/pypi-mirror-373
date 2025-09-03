from hestia_earth.schema import SchemaType
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logShouldRun
from hestia_earth.models.utils import _load_calculated_node
from hestia_earth.models.utils.blank_node import merge_blank_nodes
from hestia_earth.models.utils.feedipedia import rescale_properties_from_dryMatter
from ...utils import should_run_properties_value, average_blank_node_properties_value
from ... import MODEL

REQUIREMENTS = {
    "Cycle": {
        "animals": [{
            "@type": "Animal",
            "inputs": [{
                "@type": "Input",
                "or": {
                    "impactAssessment": {"@type": "ImpactAssessment"},
                    "properties": [{"@type": "Property", "@id": "dryMatter"}]
                }
            }]
        }]
    }
}
RETURNS = {
    "Animal": [{
        "inputs": [{
            "@type": "Input",
            "properties": [{
                "@type": "Property"
            }]
        }]
    }]
}
LOOKUPS = {
    "crop-property": "dryMatter",
    "forage-property": "dryMatter",
    "processedFoor-property": "dryMatter",
    "property": "feedipediaConversionEnum"
}
MODEL_KEY = 'properties'


def _find_related_product(input: dict):
    impact = input.get('impactAssessment')
    impact = _load_calculated_node(impact, SchemaType.IMPACTASSESSMENT) if impact else {}
    cycle = impact.get('cycle') if impact else None
    cycle = _load_calculated_node(cycle, SchemaType.CYCLE) if cycle else None
    products = (cycle or {}).get('products', [])
    return find_term_match(products, input.get('term', {}).get('@id'))


def _run_input_by_impactAssessment(cycle: dict, **log_args):
    def exec(input: dict):
        term_id = input.get('term', {}).get('@id')
        product = _find_related_product(input)
        properties = product.get('properties', [])
        all_properties = input.get('properties', [])
        new_properties = [p for p in properties if not find_term_match(all_properties, p.get('term', {}).get('@id'))]
        for prop in new_properties:
            logShouldRun(cycle, MODEL, term_id, True, property=prop.get('term', {}).get('@id'), **log_args)
        return {**input, 'properties': merge_blank_nodes(all_properties, new_properties)} if new_properties else input
    return exec


def _should_run_by_impactAssessment(input: dict):
    return bool(input.get('impactAssessment', None))


def _should_run_by_dryMatter(input: dict):
    return find_term_match(input.get('properties', []), 'dryMatter') is not None


def _run_animal(cycle: dict, animal: dict):
    # filter list of inputs to run
    inputs = [
        i for i in animal.get('inputs', []) if any([
            _should_run_by_impactAssessment(i),
            _should_run_by_dryMatter(i),
            should_run_properties_value(i)
        ])
    ]
    log_args = {'animalId': animal.get('animalId')}
    inputs = list(map(_run_input_by_impactAssessment(cycle, **log_args), inputs))
    inputs = rescale_properties_from_dryMatter(MODEL, cycle, inputs, **log_args)
    inputs = average_blank_node_properties_value(cycle, inputs, **log_args)
    return animal | {'inputs': inputs}


def run(cycle: dict):
    return list(map(lambda a: _run_animal(cycle, a), cycle.get('animals', [])))
