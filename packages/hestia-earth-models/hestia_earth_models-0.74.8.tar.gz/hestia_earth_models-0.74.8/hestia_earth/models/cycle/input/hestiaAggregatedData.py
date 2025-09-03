from hestia_earth.schema import TermTermType, NodeType
from hestia_earth.utils.model import find_primary_product, linked_node, filter_list_term_type
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.data.hestiaAggregatedData import DEFAULT_COUNTRY_ID, find_closest_impact_id
from hestia_earth.models.utils.crop import valid_site_type
from hestia_earth.models.utils.term import get_lookup_value, get_generic_crop
from hestia_earth.models.utils.aggregated import (
    should_link_input_to_impact, link_inputs_to_impact, aggregated_end_date
)

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "value": "",
            "none": {
                "impactAssessment": {"@type": "ImpactAssessment"},
                "fromCycle": "True",
                "producedInCycle": "True"
            },
            "optional": {
                "country": {"@type": "Term", "termType": "region"},
                "region": {"@type": "Term", "termType": "region"}
            }
        }],
        "optional": {
            "site": {
                "@type": "Site",
                "siteType": ["cropland", "pasture"],
                "country": {"@type": "Term", "termType": "region"}
            },
            "inputs": [{
                "@type": "Input",
                "term.@id": "seed",
                "value": "",
                "none": {
                    "impactAssessment": {"@type": "ImpactAssessment"}
                }
            }],
            "products": [{"@type": "Product", "value": "", "primary": "True"}]
        }
    }
}
RETURNS = {
    "Input": [{
        "impactAssessment": "",
        "impactAssessmentIsProxy": "True"
    }]
}
LOOKUPS = {
    "seed": "linkedImpactAssessmentTermId"
}
MODEL_ID = 'hestiaAggregatedData'
MODEL_KEY = 'impactAssessment'


def _run_seed(cycle: dict, primary_product: dict, seed_input: dict, product_term_id: str):
    country = seed_input.get('country')
    country_id = (country or {}).get('@id')

    primary_product_id = primary_product.get('term', {}).get('@id')
    default_product_id = get_generic_crop().get('@id')

    # to avoid double counting seed => aggregated impact => seed, we need to get the impact of the previous decade
    # if the data does not exist, use the aggregated impact of generic crop instead
    date = aggregated_end_date(cycle.get('endDate')) - 10

    impact_id = (
        find_closest_impact_id(product_id=product_term_id, country_id=country_id, year=date) or
        find_closest_impact_id(product_id=product_term_id, country_id=DEFAULT_COUNTRY_ID, year=date) or
        find_closest_impact_id(product_id=primary_product_id, country_id=country_id, year=date) or
        find_closest_impact_id(product_id=primary_product_id, country_id=DEFAULT_COUNTRY_ID, year=date) or
        find_closest_impact_id(product_id=default_product_id, country_id=country_id, year=date) or
        find_closest_impact_id(product_id=default_product_id, country_id=DEFAULT_COUNTRY_ID, year=date)
    )

    search_by_product_term_id = product_term_id or primary_product_id or default_product_id
    search_by_country_id = country_id or DEFAULT_COUNTRY_ID
    debugValues(cycle, model=MODEL_ID, term=seed_input.get('term', {}).get('@id'), key=MODEL_KEY,
                search_by_product_term_id=search_by_product_term_id,
                search_by_country_id=search_by_country_id,
                search_by_end_date=str(date),
                impact_assessment_id_found=impact_id)

    return seed_input | {
            MODEL_KEY: linked_node({'@type': NodeType.IMPACTASSESSMENT.value, '@id': impact_id}),
            'impactAssessmentIsProxy': True
        } if impact_id else None


def _should_run_seed(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    product_id = primary_product.get('term', {}).get('@id')
    term_type = primary_product.get('term', {}).get('termType')
    is_crop_product = term_type == TermTermType.CROP.value
    site_type_valid = valid_site_type(cycle, True)

    seed_inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.SEED)
    seed_inputs = [
        {
            'input': seed_input,
            'product-id': get_lookup_value(seed_input.get('term', {}), LOOKUPS['seed'], key=MODEL_KEY)
        }
        for seed_input in seed_inputs
    ]

    should_run = all([site_type_valid, is_crop_product, bool(seed_inputs)])

    for seed_input in seed_inputs:
        term_id = seed_input.get('input').get('term', {}).get('@id')
        linked_product_id = seed_input.get('product-id')

        logRequirements(cycle, model=MODEL_ID, term=term_id, key=MODEL_KEY,
                        site_type_valid=site_type_valid,
                        is_crop_product=is_crop_product,
                        primary_product_id=product_id,
                        linked_product_id=linked_product_id)

        logShouldRun(cycle, MODEL_ID, term_id, should_run)
        logShouldRun(cycle, MODEL_ID, term_id, should_run, key=MODEL_KEY)  # show specifically under Input

    return should_run, primary_product, seed_inputs


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    inputs = cycle.get('inputs', [])
    inputs = list(filter(should_link_input_to_impact(cycle), inputs))
    nb_inputs = len(inputs)

    logRequirements(cycle, model=MODEL_ID, key=MODEL_KEY,
                    end_date=end_date,
                    nb_inputs=nb_inputs)

    should_run = all([end_date, nb_inputs > 0])
    logShouldRun(cycle, MODEL_ID, None, should_run, key=MODEL_KEY)
    return should_run, inputs


def run(cycle: dict):
    should_run, inputs = _should_run(cycle)
    should_run_seed, primary_product, seed_inputs = _should_run_seed(cycle)
    return (
        link_inputs_to_impact(MODEL_ID, cycle, inputs) if should_run else []
    ) + (
        non_empty_list([
            _run_seed(cycle, primary_product, seed_input.get('input'), seed_input.get('product-id'))
            for seed_input in seed_inputs
        ]) if should_run_seed else []
    )
