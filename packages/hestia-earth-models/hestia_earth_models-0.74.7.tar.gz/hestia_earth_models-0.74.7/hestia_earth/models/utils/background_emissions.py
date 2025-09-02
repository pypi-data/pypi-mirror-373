from functools import reduce
from typing import Callable, Tuple
from hestia_earth.schema import TermTermType, EmissionMethodTier
from hestia_earth.utils.lookup import _is_missing_value, lookup_columns
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import flatten, non_empty_list, safe_parse_float
from hestia_earth.utils.emission import cycle_emissions_in_system_boundary

from hestia_earth.models.log import logShouldRun, logRequirements, debugValues
from . import is_from_model, _omit
from .term import get_lookup_value


def _animal_inputs(animal: dict):
    inputs = animal.get('inputs', [])
    return [(input | {'animalId': animal['animalId'], 'animal': animal.get('term', {})}) for input in inputs]


def _should_run_input(products: list):
    def should_run(input: dict):
        return all([
            # make sure Input is not a Product as well or we might double-count emissions
            find_term_match(products, input.get('term', {}).get('@id'), None) is None,
            # ignore inputs which are flagged as Product of the Cycle
            not input.get('fromCycle', False),
            not input.get('producedInCycle', False)
        ])
    return should_run


def get_background_inputs(cycle: dict, extra_inputs: list = []):
    # add all the properties of some Term that inlcude others with the mapping
    inputs = flatten(
        cycle.get('inputs', []) +
        list(map(_animal_inputs, cycle.get('animals', []))) +
        extra_inputs
    )
    return list(filter(_should_run_input(cycle.get('products', [])), inputs))


def no_gap_filled_background_emissions(
    node: dict, list_key: str = 'emissions', term_type: TermTermType = TermTermType.EMISSION
):
    blank_nodes = filter_list_term_type(node.get(list_key, []), term_type)

    def check_input(input: dict):
        input_term_id = input.get('term', {}).get('@id')
        operation_term_id = input.get('operation', {}).get('@id')
        animal_term_id = input.get('animal', {}).get('@id')

        return not any([
            is_from_model(blank_node)
            for blank_node in blank_nodes
            if all([
                any([i.get('@id') == input_term_id for i in blank_node.get('inputs', [])]),
                blank_node.get('operation', {}).get('@id') == operation_term_id,
                blank_node.get('animal', {}).get('@id') == animal_term_id
            ])
        ])

    return check_input


def _all_background_emission_term_ids(node: dict, termType: TermTermType):
    term_ids = cycle_emissions_in_system_boundary(node, termType=termType)
    background_ids = list(set([
        get_lookup_value({'termType': termType.value, '@id': term_id}, 'inputProductionGroupId')
        for term_id in term_ids
    ]))
    # make sure input production emission is itself in the system boundary
    return [term_id for term_id in background_ids if term_id in term_ids]


def log_missing_emissions(node: dict, termType: TermTermType = TermTermType.EMISSION, **log_args):
    all_emission_term_ids = _all_background_emission_term_ids(node, termType)

    def log_input(input_term_id: str, included_emission_term_ids: list, **extra_log_args):
        missing_emission_term_ids = non_empty_list([
            term_id for term_id in all_emission_term_ids if term_id not in included_emission_term_ids
        ])

        for emission_id in missing_emission_term_ids:
            # debug value on the emission itself so it appears for the input
            debugValues(node, term=emission_id,
                        value=None,
                        coefficient=None,
                        input=input_term_id,
                        **log_args,
                        **extra_log_args)
            logRequirements(node, term=input_term_id,
                            emission_id=emission_id,
                            has_emission_factor=False,
                            **log_args,
                            **extra_log_args)
            logShouldRun(node, term=input_term_id, should_run=False,
                         emission_id=emission_id,
                         **log_args,
                         **extra_log_args)
    return log_input


_KEY_TO_FIELD = {
    'inputs': 'key'
}


def _key_to_field(key: str): return _KEY_TO_FIELD.get(key) or key


def _values_from_column(index_column: str, column: str, value: str):
    values = column.split('+')
    term_id = values[0]
    value = safe_parse_float(value, default=None)
    return {
        term_id: {
            'value': value
        } | {
            _key_to_field(v.split('[')[0]): v.split('[')[1][:-1] for v in values[1:]
        }
    } if all([
        column != index_column,
        not column.startswith('ecoinvent'),
        not column.startswith('ecoalim'),
        not _is_missing_value(value)
    ]) else {}


def convert_background_lookup(lookup, index_column: str):
    columns = lookup_columns(lookup)
    return {
        row[index_column]: reduce(
            lambda prev, curr: prev | _values_from_column(index_column, curr, row[curr]),
            columns,
            {}
        )
        for row in lookup
    }


def parse_term_id(term_id: str): return term_id.split('-')[0]


def join_term_id(term_id: str, data: dict):
    return '-'.join(non_empty_list([term_id] + list(_omit(data, ['value']).values())))


def _process_mapping(
    node: dict,
    input: dict,
    term_type: TermTermType,
    extract_mapping: Callable[[Tuple, TermTermType], Tuple[dict, float]],
    **log_args
) -> dict:
    input_term_id = input.get('term', {}).get('@id')
    operation_term_id = input.get('operation', {}).get('@id')
    animal_term_id = input.get('animal', {}).get('@id')

    def add(prev: dict, mapping: Tuple):
        values, coefficient = extract_mapping(mapping, term_type)
        for term_id, data in values:
            # log run on each node so we know it did run
            logShouldRun(node, term=input_term_id, should_run=True,
                         methodTier=EmissionMethodTier.BACKGROUND.value,
                         emission_id=term_id,
                         **log_args)
            debugValues(node, term=term_id,
                        value=data.get('value'),
                        coefficient=coefficient,
                        input=input_term_id,
                        operation=operation_term_id,
                        animal=animal_term_id,
                        **log_args)
            group_id = join_term_id(term_id, data)
            prev[group_id] = prev.get(group_id, []) + [data | {'coefficient': coefficient}]
        return prev
    return add


def process_input_mappings(
    node: dict,
    input: dict,
    mappings: list,
    term_type: TermTermType,
    extract_mapping: Callable[[tuple, TermTermType], Tuple[dict, float]],
    **log_args
):
    return reduce(_process_mapping(node, input, term_type, extract_mapping, **log_args), mappings, {})
