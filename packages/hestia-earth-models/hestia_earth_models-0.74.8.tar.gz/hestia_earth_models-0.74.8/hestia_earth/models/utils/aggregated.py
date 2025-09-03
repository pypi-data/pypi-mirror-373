import math
from hestia_earth.schema import NodeType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.model import find_term_match, linked_node
from hestia_earth.utils.tools import safe_parse_date, non_empty_list

from hestia_earth.models.log import debugValues, logShouldRun
from hestia_earth.models.data.hestiaAggregatedData import DEFAULT_COUNTRY_ID, find_closest_impact_id
from . import current_year

MODEL_KEY = 'impactAssessment'


def aggregated_end_date(end_date: str):
    year = safe_parse_date(end_date).year
    return min([round(math.floor(year / 10) * 10) + 9, current_year()])


def _link_input_to_impact(model: str, cycle: dict, date: int, **log_args):
    def run(input: dict):
        term = input.get('term', {})
        term_id = term.get('@id')
        country = input.get('country')
        country_id = (country or {}).get('@id')
        impact_id = (
            find_closest_impact_id(product_id=term_id, country_id=country_id, year=date) or
            find_closest_impact_id(product_id=term_id, country_id=DEFAULT_COUNTRY_ID, year=date)
        )

        search_by_country_id = country_id or DEFAULT_COUNTRY_ID
        debugValues(cycle, model=model, term=term_id, key=MODEL_KEY, **log_args,
                    search_by_input_term_id=term_id,
                    search_by_country_id=search_by_country_id,
                    search_by_end_date=str(date),
                    impact_assessment_id_found=impact_id)

        should_run = all([impact_id])
        logShouldRun(cycle, model, term_id, should_run, **log_args)
        logShouldRun(cycle, model, term_id, should_run, key=MODEL_KEY, **log_args)  # show specifically under Input

        return input | {
            MODEL_KEY: linked_node({'@type': NodeType.IMPACTASSESSMENT.value, '@id': impact_id}),
            'impactAssessmentIsProxy': True
        } if impact_id else None
    return run


def link_inputs_to_impact(model: str, cycle: dict, inputs: list, **log_args):
    date = aggregated_end_date(cycle.get('endDate'))
    return non_empty_list(map(_link_input_to_impact(model, cycle, date, **log_args), inputs))


def _should_aggregate_input(term: dict):
    lookup = download_lookup(f"{term.get('termType')}.csv", True)
    value = get_table_value(lookup, 'termid', term.get('@id'), column_name('skipAggregation'))
    return True if value is None or value == '' else not value


def should_link_input_to_impact(cycle: dict):
    def should_run(input: dict):
        term = input.get('term', {})
        return all([
            _should_aggregate_input(term),
            # make sure Input is not a Product as well or we might double-count emissions
            find_term_match(cycle.get('products', []), term.get('@id'), None) is None,
            not input.get('impactAssessment'),
            # ignore inputs which are flagged as Product of the Cycle
            not input.get('fromCycle', False),
            not input.get('producedInCycle', False)
        ])
    return should_run
