from hestia_earth.schema import InputStatsDefinition

from hestia_earth.models.log import logShouldRun
from hestia_earth.models.utils.product import find_by_product
from hestia_earth.models.utils.transformation import previous_transformation


def replace_input_field(node: dict, model: str, input: dict, product: dict, share: float, field: str):
    term_id = input.get('term', {}).get('@id')
    product_value = (product or {}).get(field, [])
    should_run = all([len(product_value) > 0])
    if product and field in product:
        logShouldRun(node, model, term_id, should_run, key=field)
    return {
        **input,
        field: [v * share / 100 for v in product_value],
        'statsDefinition': InputStatsDefinition.MODELLED.value
    } if should_run else input


def run_transformation(cycle: dict, model: str, field: str):
    def run(transformations: list, transformation: dict):
        previous = previous_transformation(cycle, transformations, transformation)
        share = transformation.get('transformedShare', 100)
        transformation['inputs'] = [
            replace_input_field(previous, model, i, find_by_product(previous, i), share, field)
            for i in transformation.get('inputs', [])
        ]
        return transformations + [transformation]
    return run
