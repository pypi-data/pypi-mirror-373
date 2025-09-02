from haversine import haversine
from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues
from hestia_earth.models.utils.method import include_methodModel
from hestia_earth.models.utils.term import download_term
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "country": {"@type": "Term", "termType": "region"},
            "transport": [{"@type": "Transport"}]
        }],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        }
    }
}
RETURNS = {
    "Input": [{
        "transport": [{
            "@type": "Transport",
            "distance": ""
        }]
    }]
}
MODEL_KEY = 'distance'


def _run_transport(cycle: dict, distance_kms: float):
    def exec(transport: dict):
        return include_methodModel(transport | {
            MODEL_KEY: distance_kms
        }, MODEL) if _should_run_transport(cycle, transport) else transport
    return exec


def _should_run_transport(cycle: dict, transport: dict):
    term_id = transport.get('term', {}).get('@id')
    value_not_set = transport.get(MODEL_KEY) is None

    should_run = all([value_not_set])

    # skip logs if we don't run the model to avoid showing an "error"
    if should_run:
        logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY,
                        value_not_set=value_not_set)
        logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY)
    return should_run


def _run_input(cycle: dict, site_country: dict):
    def exec(input: dict):
        term_id = input.get('term', {}).get('@id')
        input_country = download_term(input.get('country', {}).get('@id'), TermTermType.REGION)
        distance_kms = haversine(
            (site_country.get('latitude'), site_country.get('longitude')),
            (input_country.get('latitude'), input_country.get('longitude'))
        )
        debugValues(cycle, model=MODEL, term=term_id, key=MODEL_KEY,
                    distance_kms=distance_kms)
        transport = input.get('transport')
        return {
            **input,
            **({'transport': list(map(_run_transport(cycle, distance_kms), transport))} if transport else {})
        }
    return exec


def _should_run_input(site_country_id: str):
    def exec(input: dict):
        input_country = input.get('country', {}) or {}
        input_country_id = input_country.get('@id')
        input_country = download_term(input_country_id, TermTermType.REGION)
        has_transports = len(input.get('transport', [])) > 0
        should_run = input_country and all([
            input_country.get('latitude'), input_country.get('latitude'),
            has_transports, input_country_id != site_country_id
        ])
        return should_run
    return exec


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    inputs = list(filter(_should_run_input(country_id), cycle.get('inputs', [])))
    # download full term to get coordinates only if there is anything to run
    country = download_term(country_id, TermTermType.REGION) if len(inputs) > 0 else {}

    # can only run if the site country has centroid coordinates
    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    latitude=country.get('latitude'),
                    longitude=country.get('longitude'),
                    has_inputs_transport=len(inputs) > 0)
    should_run = all([country.get('latitude'), country.get('latitude'), len(inputs) > 0])
    logShouldRun(cycle, MODEL, None, should_run, key=MODEL_KEY)
    return should_run, country, inputs


def run(cycle: dict):
    should_run, country, inputs = _should_run(cycle)
    return non_empty_list(map(_run_input(cycle, country), inputs)) if should_run else []
