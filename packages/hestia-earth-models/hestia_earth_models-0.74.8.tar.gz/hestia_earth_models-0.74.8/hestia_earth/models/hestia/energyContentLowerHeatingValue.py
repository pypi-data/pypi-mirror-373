from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.property import _new_property, get_node_property
from hestia_earth.models.utils.term import get_wood_fuel_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "term.@id": ["woodFuel", "woodPellets"],
            "properties": [{"@type": "Property", "value": "", "term.@id": "dryMatter"}]
        }]
    }
}
RETURNS = {
    "Input": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
TERM_ID = 'energyContentLowerHeatingValue'
PROPERTY_KEY = 'dryMatter'
DRY_VALUE = 19.2  # Bone dry wood has an energy content of 19.2 MJ/kg


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    return prop


def _run(cycle: dict, inputs: list):
    def run_input(input: dict):
        term_id = input.get('term', {}).get('@id')
        dry_matter = get_node_property(input, PROPERTY_KEY).get('value')
        moisture_content = 100 - dry_matter
        value = DRY_VALUE - (0.2164 * moisture_content)
        logShouldRun(cycle, MODEL, term_id, True, property=TERM_ID)
        return {**input, 'properties': input.get('properties', []) + [_property(round(value, 2))]}

    return non_empty_list(map(run_input, inputs))


def _should_run_input(cycle: dict):
    def should_run_input(input: dict):
        term_id = input.get('term', {}).get('@id')
        prop_value = get_node_property(input, PROPERTY_KEY, find_default_property=False).get('value')

        logRequirements(cycle, model=MODEL, term=term_id, property=TERM_ID,
                        dryMatter=prop_value)

        should_run = all([prop_value is not None])
        logShouldRun(cycle, MODEL, term_id, should_run, property=TERM_ID)
        return should_run
    return should_run_input


def run(cycle: dict):
    term_ids = get_wood_fuel_terms()
    inputs = [input for input in cycle.get('inputs', []) if input.get('term', {}).get('@id') in term_ids]
    inputs = list(filter(_should_run_input(cycle), inputs))
    return _run(cycle, inputs)
