from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import extract_grouped_data
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import merge_blank_nodes
from hestia_earth.models.utils.property import _new_property, node_has_no_property
from hestia_earth.models.utils.productivity import PRODUCTIVITY, get_productivity
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.lookup import get_region_lookup_value
from .. import MODEL


def _get_practice(term_id: str, animal: dict, practice_column: str):
    term = animal.get('term', {})
    value = get_lookup_value(term, practice_column, model=MODEL, term=term_id)
    practice_ids = non_empty_list((value or '').split(';'))
    return next(
        (p for p in animal.get('practices', []) if p.get('term', {}).get('@id') in practice_ids),
        {}
    )


def productivity_lookup_value(term_id: str, lookup: str, country: dict, animal: dict):
    country_id = country.get('@id')
    productivity_key = get_productivity(country)
    column = animal.get('term').get('@id')
    value = get_region_lookup_value(f"{lookup}.csv", country_id, column, model=MODEL, term=term_id)
    return safe_parse_float(
        extract_grouped_data(value, productivity_key.value) or
        extract_grouped_data(value, PRODUCTIVITY.HIGH.value),  # defaults to high if low is not found
        default=None
    )


def map_live_animals_by_productivity_lookup(term_id: str, cycle: dict, lookup_col: str, practice_column: str = None):
    country = cycle.get('site', {}).get('country', {})
    live_animals = filter_list_term_type(cycle.get('animals', []), TermTermType.LIVEANIMAL)
    live_animals = list(filter(node_has_no_property(term_id), live_animals))
    return [{
        'animal': animal,
        'value': productivity_lookup_value(term_id, lookup_col, country, animal)
    } | ({
        'practice': _get_practice(term_id, animal, practice_column)
    } if practice_column else {}) for animal in live_animals]


def should_run_by_productivity_lookup(
    term_id: str,
    cycle: dict,
    lookup_col: str,
    practice_column: str = None
):
    country = cycle.get('site', {}).get('country', {})
    country_id = country.get('@id')
    live_animals_with_value = map_live_animals_by_productivity_lookup(term_id, cycle, lookup_col, practice_column)

    def _should_run_animal(value: dict):
        animal = value.get('animal')
        lookup_value = value.get('value')
        practice = value.get('practice')
        animal_term_id = animal.get('term').get('@id')

        logRequirements(cycle, model=MODEL, term=animal_term_id, animalId=animal.get('animalId'), property=term_id,
                        country_id=country_id,
                        **({
                            lookup_col.replace('-', '_'): lookup_value
                        } | ({
                            'practice': practice.get('term', {}).get('@id')
                        } if practice_column else {})))

        should_run = all([
            country_id,
            not practice_column or bool(practice),
            lookup_value is not None
        ])
        logShouldRun(cycle, MODEL, animal_term_id, should_run, animalId=animal.get('animalId'), property=term_id)

        return should_run

    return list(filter(_should_run_animal, live_animals_with_value))


def _property(term_id: str, value: float):
    prop = _new_property(term_id, MODEL)
    prop['value'] = value
    return prop


def run_animal_by_productivity(term_id: str, include_practice: bool = False):
    def run(data: dict):
        animal = data.get('animal')
        value = data.get('value')
        practice = data.get('practice')
        return animal | ({
            'practices': [
                (
                    p | ({
                        'properties': merge_blank_nodes(p.get('properties', []), [_property(term_id, value)])
                    } if p.get('term', {}).get('@id') == practice.get('term', {}).get('@id') else {})
                ) for p in animal.get('practices', [])
            ]
        } if include_practice else {
            'properties': merge_blank_nodes(animal.get('properties', []), [_property(term_id, value)])
        })
    return run
