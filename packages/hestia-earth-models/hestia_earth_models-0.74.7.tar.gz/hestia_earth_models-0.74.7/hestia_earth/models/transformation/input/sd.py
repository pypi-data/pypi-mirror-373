from functools import reduce
from hestia_earth.schema import NodeType

from hestia_earth.models.log import logShouldRun
from .utils import run_transformation
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "sd": ""}],
        "transformations": [
            {
                "@type": "Transformation",
                "transformedShare": "",
                "inputs": [{"@type": "Input"}]
            }
        ]
    }
}
RETURNS = {
    "Transformation": [{
        "inputs": [{
            "@type": "Input",
            "sd": "",
            "statsDefinition": "modelled"
        }]
    }]
}
MODEL_KEY = 'sd'
MODEL_LOG = '/'.join([MODEL, 'input', MODEL_KEY])


def _should_run(cycle: dict):
    node_type = cycle.get('type', cycle.get('@type'))
    has_transformations = len(cycle.get('transformations', [])) > 0
    should_run = all([node_type == NodeType.CYCLE.value, has_transformations])
    logShouldRun(cycle, MODEL_LOG, None, should_run)
    return should_run


def run(cycle: dict):
    should_run = _should_run(cycle)
    transformations = cycle.get('transformations', []) if should_run else []
    return reduce(run_transformation(cycle, MODEL_LOG, MODEL_KEY), transformations, [])
