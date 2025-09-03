from hestia_earth.utils.tools import list_sum
from hestia_earth.utils.emission import cycle_emissions_in_system_boundary

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _include
from hestia_earth.models.utils.impact_assessment import get_product, convert_value_from_cycle
from hestia_earth.models.utils.indicator import _new_indicator
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "product": {"@type": "Product"},
        "cycle": {
            "@type": "Cycle",
            "products": [{
                "@type": "Product",
                "primary": "True",
                "value": "> 0",
                "economicValueShare": "> 0"
            }],
            "emissions": [{"@type": "Emission", "value": ""}]
        }
    }
}
RETURNS = {
    "Indicator": [{
        "term": "",
        "value": "",
        "methodTier": ""
    }]
}
MODEL_KEY = 'emissions'


def _indicator(impact_assessment: dict, product: dict):
    def run(emission: dict):
        term_id = emission.get('term', {}).get('@id')
        value = convert_value_from_cycle(
            impact_assessment, product, list_sum(emission.get('value', [0])), model=MODEL, term_id=term_id
        )

        indicator = _new_indicator(emission.get('term', {}), emission.get('methodModel'))
        indicator['value'] = value
        indicator['methodTier'] = emission.get('methodTier')

        if len(emission.get('inputs', [])):
            indicator['inputs'] = emission['inputs']

        return indicator | _include(emission, ['animals', 'operation', 'transformation', 'country', 'key'])
    return run


def _log_missing_emissions(impact_assessment: dict, emissions: list):
    term_ids = cycle_emissions_in_system_boundary(cycle=impact_assessment.get('cycle', {}))
    emission_ids = list(map(lambda e: e.get('term', {}).get('@id'), emissions))
    missing_term_ids = [term_id for term_id in term_ids if term_id not in emission_ids]
    for term_id in missing_term_ids:
        logRequirements(impact_assessment, model=MODEL, term=term_id,
                        present_in_cycle=False)
        logShouldRun(impact_assessment, MODEL, term_id, should_run=False)


def _should_run_emission(impact_assessment: dict):
    product = get_product(impact_assessment)

    def exec(emission: dict):
        term_id = emission.get('term', {}).get('@id')
        has_value = convert_value_from_cycle(
            impact_assessment, product, list_sum(emission.get('value', [0])), model=MODEL, term_id=term_id
        ) is not None
        not_deleted = emission.get('deleted', False) is not True

        logRequirements(impact_assessment, model=MODEL, term=term_id,
                        has_value=has_value,
                        emission_included_in_models=not_deleted)

        should_run = all([has_value, not_deleted])
        logShouldRun(impact_assessment, MODEL, term_id, should_run)
        return should_run
    return exec


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment)
    product_id = product.get('term', {}).get('@id')
    logRequirements(impact_assessment, model=MODEL, key=MODEL_KEY,
                    product=product_id)
    should_run = product_id is not None
    logShouldRun(impact_assessment, MODEL, None, should_run, key=MODEL_KEY)
    return should_run, product


def run(impact_assessment: dict):
    should_run, product = _should_run(impact_assessment)
    emissions = impact_assessment.get('cycle', {}).get(MODEL_KEY, []) if should_run else []
    emissions = list(filter(_should_run_emission(impact_assessment), emissions))
    _log_missing_emissions(impact_assessment, emissions)
    return list(map(_indicator(impact_assessment, product), emissions))
