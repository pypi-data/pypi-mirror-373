from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.model import find_term_match, linked_node, filter_list_term_type
from hestia_earth.utils.tools import list_sum, non_empty_list, list_average, flatten
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

from hestia_earth.models.log import logger
from . import _filter_list_term_unit, _load_calculated_node, group_by
from .constant import Units
from .blank_node import get_total_value, get_total_value_converted, get_lookup_value
from .term import download_term
from .method import include_model


def _new_input(term, model=None):
    node = {'@type': SchemaType.INPUT.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(term))
    return include_model(node, model)


def load_impacts(inputs: list):
    """
    Load and return `Input`s that have an `impactAssessment`.

    Parameters
    ----------
    inputs : list
        A list of `Input`.

    Returns
    -------
    list
        The filtered list of `Input` with full `impactAssessment` node.
    """
    def _load_impact(input: dict):
        impact = input.get('impactAssessment')
        impact = _load_calculated_node(impact, SchemaType.IMPACTASSESSMENT) if impact else None
        return {**input, 'impactAssessment': impact} if impact else None

    # filter by inputs that have an impactAssessment
    return non_empty_list(map(_load_impact, inputs))


def sum_input_impacts(inputs: list, term_id: str) -> float:
    """
    Load and return the sum of the `emissionsResourceUse` value linked to each `Input`.

    Parameters
    ----------
    inputs : list
        A list of `Input`.

    Returns
    -------
    float
        The total impact of the `Input` for the `Term` or `None` if none found.
    """
    def _input_value(input: dict):
        impact = input.get('impactAssessment', {})
        indicators = impact.get('emissionsResourceUse', []) + impact.get('impacts', [])
        value = find_term_match(indicators, term_id).get('value', None)
        input_value = list_sum(input.get('value', [0]))
        logger.debug('input with impact, term=%s, input=%s, input value=%s, impact value=%s',
                     term_id, input.get('term', {}).get('@id'), input_value, value)
        return value * input_value if value is not None else None

    inputs = load_impacts(inputs)
    logger.debug('term=%s, nb inputs impact=%s', term_id, len(inputs))
    return list_sum(non_empty_list(map(_input_value, inputs)), None)


def match_lookup_value(input: dict, col_name: str, col_value):
    """
    Check if input matches lookup value.

    Parameters
    ----------
    inputs : dict
        An `Input`.
    col_name : str
        The name of the column in the lookup table.
    col_value : Any
        The cell value matching the row/column in the lookup table.

    Returns
    -------
    list
        A list of `Input`.
    """
    term_type = input.get('term', {}).get('termType')
    lookup = download_lookup(f"{term_type}.csv")
    term_id = input.get('term', {}).get('@id')
    return get_table_value(lookup, 'termid', term_id, column_name(col_name)) == col_value


def get_feed_inputs(cycle: dict):
    inputs = flatten(cycle.get('inputs', []) + [a.get('inputs', []) for a in cycle.get('animals', [])])
    return [input for input in inputs if all([
        list_sum(input.get('value', [])) > 0,
        input.get('term', {}).get('units') == Units.KG.value,
        input.get('isAnimalFeed', False) is True,
        # handle feed food additives
        input.get('term', {}).get('termType') != TermTermType.FEEDFOODADDITIVE.value or
        bool(get_lookup_value(input.get('term', {}), 'hasEnergyContent'))
    ])]


def total_excreta_tan(inputs: list):
    """
    Get the total excreta ammoniacal nitrogen from all the excreta inputs in `kg N` units.
    Will use the `totalAmmoniacalNitrogenContentAsN` property to convert to kg of TAN.

    Parameters
    ----------
    inputs : list
        List of `Input`s.

    Returns
    -------
    float
        The total value as a number.
    """
    excreta = filter_list_term_type(inputs, TermTermType.EXCRETA)
    excreta_kg_N = _filter_list_term_unit(excreta, Units.KG_N)
    return list_sum(get_total_value_converted(excreta_kg_N, 'totalAmmoniacalNitrogenContentAsN'), None)


def total_excreta(inputs: list, units=Units.KG_N):
    """
    Get the total excreta from all the excreta inputs in `kg N` units.

    Parameters
    ----------
    inputs : list
        List of `Input`s.
    units: Units
        The units of the excreta. Can be either `kg`, `kg N` or `kg VS`.

    Returns
    -------
    float
        The total value as a number.
    """
    excreta = filter_list_term_type(inputs, TermTermType.EXCRETA)
    excreta = _filter_list_term_unit(excreta, units)
    return list_sum(get_total_value(excreta), None)


def get_total_irrigation_m3(cycle: dict):
    irrigation_inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.WATER)
    return sum([list_average(i.get('value')) for i in irrigation_inputs if len(i.get('value', [])) > 0])


def _group_inputs(inputs: list):
    grouped_inputs = group_by(inputs, ['input.term.@id'])
    return [
        inputs[0] | {'value': list_sum(flatten([v.get('input-value') for v in inputs]))}
        for inputs in grouped_inputs.values()
    ]


def _input_data(input: dict):
    return {
        'input': input,
        'input-value': list_sum(input.get('value'), default=None),
        'has-linked-impact-assessment': bool(input.get('impactAssessment')),
        'is-fromCycle': input.get('fromCycle', False),
        'is-producedInCycle': input.get('producedInCycle', False)
    }


def unique_background_inputs(cycle: dict):
    inputs = non_empty_list(map(_input_data, cycle.get('inputs', [])))

    # sum up inputs with the same id
    return _group_inputs([
        v for v in inputs
        if all([
            v.get('input-value') or -1 > 0,
            not v.get('has-linked-impact-assessment'),
            not v.get('is-fromCycle'),
            not v.get('is-producedInCycle')
        ])
    ])
