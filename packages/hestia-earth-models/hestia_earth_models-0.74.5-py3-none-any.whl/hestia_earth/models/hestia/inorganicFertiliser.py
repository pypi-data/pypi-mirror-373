from hestia_earth.schema import InputStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import flatten, non_empty_list, safe_parse_float, list_sum

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.inorganicFertiliser import get_term_lookup
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "term.termType": "inorganicFertiliser",
            "value": "> 0"
        }]
    }
}
RETURNS = {
    "Input": [{
        "term.termType": "inorganicFertiliser",
        "value": "",
        "min": "",
        "max": "",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "inorganicFertiliser": [
        "complementaryTermIds",
        "nitrogenContent", "nitrogenContent-min", "nitrogenContent-max",
        "phosphateContentAsP2O5", "phosphateContentAsP2O5-min", "phosphateContentAsP2O5-max",
        "potassiumContentAsK2O", "potassiumContentAsK2O-min", "potassiumContentAsK2O-max"
    ]
}
MODEL_KEY = 'inorganicFertiliser'
MODEL_LOG = '/'.join([MODEL, MODEL_KEY])

UNITS = [
    Units.KG_P2O5.value,
    Units.KG_K2O.value
]
VALUE_BY_UNIT = {
    Units.KG_N.value: {
        Units.KG_K2O.value: lambda data: (
            data.get('value') / data.get('nitrogenContent-divide')
        ) * data.get('potassiumContentAsK2O-multiply'),
        Units.KG_P2O5.value: lambda data: (
            data.get('value') / data.get('nitrogenContent-divide')
        ) * data.get('phosphateContentAsP2O5-multiply')
    },
    Units.KG_K2O.value: {
        Units.KG_N.value: lambda data: (
            data.get('value') / data.get('potassiumContentAsK2O-divide')
        ) * data.get('nitrogenContent-multiply'),
        Units.KG_P2O5.value: lambda data: (
            data.get('value') / data.get('potassiumContentAsK2O-divide')
        ) * data.get('phosphateContentAsP2O5-multiply')
    },
    Units.KG_P2O5.value: {
        Units.KG_N.value: lambda data: (
            data.get('value') / data.get('phosphateContentAsP2O5-divide')
        ) * data.get('nitrogenContent-multiply'),
        Units.KG_K2O.value: lambda data: (
            data.get('value') / data.get('phosphateContentAsP2O5-divide')
        ) * data.get('potassiumContentAsK2O-multiply')
    }
}


def _input(term_id: str, value: float, min: float = None, max: float = None):
    input = _new_input(term_id, MODEL)
    input['value'] = [value]
    if min is not None:
        input['min'] = [min]
        input['statsDefinition'] = InputStatsDefinition.MODELLED.value
    if max is not None:
        input['max'] = [max]
        input['statsDefinition'] = InputStatsDefinition.MODELLED.value
    return input


def _include_term_ids(term_id: str):
    return non_empty_list((get_term_lookup(term_id, LOOKUPS['inorganicFertiliser'][0]) or '').split(';'))


def _run_input(cycle: dict, input: dict):
    term_id = input.get('term', {}).get('@id')
    input_term_ids = _include_term_ids(term_id)
    nitrogenContent = safe_parse_float(get_term_lookup(term_id, 'nitrogenContent'), default=0)
    nitrogenContent_min = safe_parse_float(get_term_lookup(term_id, 'nitrogenContent-min'), default=None)
    nitrogenContent_max = safe_parse_float(get_term_lookup(term_id, 'nitrogenContent-max'), default=None)
    phosphateContentAsP2O5 = safe_parse_float(get_term_lookup(term_id, 'phosphateContentAsP2O5'), default=0)
    phosphateContentAsP2O5_min = safe_parse_float(get_term_lookup(term_id, 'phosphateContentAsP2O5-min'), default=None)
    phosphateContentAsP2O5_max = safe_parse_float(get_term_lookup(term_id, 'phosphateContentAsP2O5-max'), default=None)
    potassiumContentAsK2O = safe_parse_float(get_term_lookup(term_id, 'potassiumContentAsK2O'), default=0)
    potassiumContentAsK2O_min = safe_parse_float(get_term_lookup(term_id, 'potassiumContentAsK2O-min'), default=None)
    potassiumContentAsK2O_max = safe_parse_float(get_term_lookup(term_id, 'potassiumContentAsK2O-max'), default=None)

    from_units = input.get('term', {}).get('units')
    input_value = list_sum(input.get('value'))
    min_values = non_empty_list([nitrogenContent_min, phosphateContentAsP2O5_min, potassiumContentAsK2O_min])
    max_values = non_empty_list([nitrogenContent_max, phosphateContentAsP2O5_max, potassiumContentAsK2O_max])

    def include_input(input_term_id: str):
        to_units = Units.KG_N.value if input_term_id.endswith('KgN') else (
            Units.KG_K2O.value if input_term_id.endswith('KgK2O') else Units.KG_P2O5.value
        )

        debugValues(cycle, model=MODEL_LOG, term=input_term_id,
                    from_input_id=term_id,
                    from_units=from_units,
                    to_units=to_units,
                    input_value=input_value,
                    nitrogenContent=nitrogenContent,
                    nitrogenContent_min=nitrogenContent_min,
                    nitrogenContent_max=nitrogenContent_max,
                    phosphateContentAsP2O5=phosphateContentAsP2O5,
                    phosphateContentAsP2O5_min=phosphateContentAsP2O5_min,
                    phosphateContentAsP2O5_max=phosphateContentAsP2O5_max,
                    potassiumContentAsK2O=potassiumContentAsK2O,
                    potassiumContentAsK2O_min=potassiumContentAsK2O_min,
                    potassiumContentAsK2O_max=potassiumContentAsK2O_max)

        converter = VALUE_BY_UNIT.get(from_units, {}).get(to_units, lambda *args: None)
        value = converter(
            {
                'value': input_value,
                'nitrogenContent-multiply': nitrogenContent,
                'nitrogenContent-divide': nitrogenContent,
                'phosphateContentAsP2O5-multiply': phosphateContentAsP2O5,
                'phosphateContentAsP2O5-divide': phosphateContentAsP2O5,
                'potassiumContentAsK2O-multiply': potassiumContentAsK2O,
                'potassiumContentAsK2O-divide': potassiumContentAsK2O,
            }
        )
        min = converter(
            {
                'value': input_value,
                'nitrogenContent-multiply': nitrogenContent_min,
                'nitrogenContent-divide': nitrogenContent_max,
                'phosphateContentAsP2O5-multiply': phosphateContentAsP2O5_min,
                'phosphateContentAsP2O5-divide': phosphateContentAsP2O5_max,
                'potassiumContentAsK2O-multiply': potassiumContentAsK2O_min,
                'potassiumContentAsK2O-divide': potassiumContentAsK2O_max,
            }
        ) if len(min_values) >= 2 else None
        max = converter(
            {
                'value': input_value,
                'nitrogenContent-multiply': nitrogenContent_max,
                'nitrogenContent-divide': nitrogenContent_min,
                'phosphateContentAsP2O5-multiply': phosphateContentAsP2O5_max,
                'phosphateContentAsP2O5-divide': phosphateContentAsP2O5_min,
                'potassiumContentAsK2O-multiply': potassiumContentAsK2O_max,
                'potassiumContentAsK2O-divide': potassiumContentAsK2O_min,
            }
        ) if len(max_values) >= 2 else None

        return _input(input_term_id, value, min, max) if value else None

    return list(map(include_input, input_term_ids))


def _should_run_input(cycle: dict, input: dict):
    term_id = input.get('term', {}).get('@id')
    has_value = list_sum(input.get('value', [])) > 0
    nitrogenContent = safe_parse_float(get_term_lookup(term_id, 'nitrogenContent'), default=None)
    phosphateContentAsP2O5 = safe_parse_float(get_term_lookup(term_id, 'phosphateContentAsP2O5'), default=None)
    potassiumContentAsK2O = safe_parse_float(get_term_lookup(term_id, 'potassiumContentAsK2O'), default=None)

    # skip inputs that already have all the inlcuded term with a value
    inputs = cycle.get('inputs', [])
    include_term_ids = [
        term_id for term_id in _include_term_ids(term_id)
        if len(find_term_match(inputs, term_id).get('value', [])) == 0
    ]
    should_run = all([
        has_value,
        len(include_term_ids) > 0,
        len(non_empty_list([nitrogenContent, phosphateContentAsP2O5, potassiumContentAsK2O])) >= 2
    ])

    for term_id in include_term_ids:
        logRequirements(cycle, model=MODEL_LOG, term=term_id, model_key=MODEL_KEY,
                        nitrogenContent=nitrogenContent,
                        phosphateContentAsP2O5=phosphateContentAsP2O5,
                        potassiumContentAsK2O=potassiumContentAsK2O)

        logShouldRun(cycle, MODEL_LOG, term_id, should_run, model_key=MODEL_KEY)
    return should_run


def run(cycle: dict):
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.INORGANICFERTILISER)
    inputs = [i for i in inputs if _should_run_input(cycle, i)]
    return non_empty_list(flatten([_run_input(cycle, i) for i in inputs]))
