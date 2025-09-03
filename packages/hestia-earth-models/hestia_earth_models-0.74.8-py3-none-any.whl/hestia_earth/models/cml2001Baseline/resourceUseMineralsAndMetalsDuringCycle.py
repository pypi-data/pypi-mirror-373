from collections import defaultdict
from itertools import groupby
from typing import Tuple
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.blank_node import _sum_nodes_value
from hestia_earth.models.utils.indicator import _new_indicator
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [
            {
                "@type": "Input",
                "term.units": "kg",
                "term.termType": ["material", "soilAmendment", "otherInorganicChemical"]}
        ]
    }
}

RETURNS = {
    "Indicator": [{
        "value": "",
        "inputs": ""
    }]
}
TERM_ID = 'resourceUseMineralsAndMetalsDuringCycle'

authorised_term_types = [TermTermType.MATERIAL, TermTermType.SOILAMENDMENT, TermTermType.OTHERINORGANICCHEMICAL]


def _indicator(value: list[float], cycle_input: dict):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = list_sum(value)
    indicator['inputs'] = [cycle_input]
    return indicator


def _run(grouped_abiotic_terms: dict):
    indicators = [
        _indicator(value=_sum_nodes_value(abiotic_term_group_vals),
                   cycle_input=abiotic_term_group_vals[0]['term'])
        for abiotic_term_group_vals in grouped_abiotic_terms.values()
    ]
    return indicators


def _should_run(cycle: dict) -> Tuple[bool, dict]:
    abiotic_terms = filter_list_term_type(cycle.get('inputs', []), authorised_term_types)
    abiotic_terms_valid_units = _filter_list_term_unit(abiotic_terms, Units.KG)

    has_abiotic_terms = bool(abiotic_terms)
    has_valid_terms = bool(abiotic_terms_valid_units)

    grouped_abiotic_terms = defaultdict(list)
    for k, v in groupby(abiotic_terms_valid_units,
                        key=lambda x: (x['term']['@id'], x['term']['units'], x['term']['termType'])):
        grouped_abiotic_terms[k].extend(list(v))

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_abiotic_terms=has_abiotic_terms,
                    has_valid_terms=has_valid_terms,
                    )

    should_run = all([has_valid_terms])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, grouped_abiotic_terms


def run(cycle: dict):
    should_run, grouped_abiotic_terms = _should_run(cycle)
    return _run(grouped_abiotic_terms) if should_run else []
