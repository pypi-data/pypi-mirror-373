from functools import reduce
from hestia_earth.schema import TermTermType, EmissionMethodTier, SiteSiteType
from hestia_earth.utils.lookup import (
    download_lookup, column_name, extract_grouped_data_closest_date, find_term_ids_by
)
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list, flatten, list_sum, safe_parse_float
from hestia_earth.utils.emission import cycle_emissions_in_system_boundary

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table, debugValues
from hestia_earth.models.utils import _omit, group_by
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.site import valid_site_type
from hestia_earth.models.utils.cycle import cycle_end_year
from hestia_earth.models.utils.crop import get_crop_lookup_value, get_landCover_term_id
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.lookup import get_region_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.product": "True",
        "endDate": "",
        "inputs": [{
            "@type": "Input",
            "term.termType": "seed",
            "value": "> 0",
            "none": {
                "impactAssessment": {"@type": "ImpactAssessment"},
                "fromCycle": "True",
                "producedInCycle": "True"
            }
        }],
        "products": [{
            "@type": "Product",
            "term.termType": "crop",
            "optional": {
                "economicValueShare": "> 0"
            }
        }],
        "site": {
            "@type": "Site",
            "siteType": ["cropland", "glass or high accessible cover"],
            "country": {"@type": "Term", "termType": "region"}
        },
        "emissions": [{"@type": "Emission", "value": ""}]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "inputs": "",
        "methodTier": "background"
    }]
}
LOOKUPS = {
    "region-crop-cropGroupingFaostatProduction-yield": "",
    "crop": [
        "correspondingSeedTermIds",
        "cropGroupingFaostatProduction",
        "cropGroupingFaostatProductionProxy",
        "global_economic_value_share",
        "landCoverTermId"
    ],
    "emission": "inputProductionGroupId"
}
MODEL_KEY = 'seed_emissions'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [round(value, 7)]
    emission['inputs'] = [input]
    emission['methodTier'] = TIER
    return emission


def _run_emission(
    cycle: dict, economicValueShare: float, total_yield: float, seed_input: dict, term_id: str, emission_value: float
):
    input_term = seed_input.get('term', {})
    input_term_id = input_term.get('@id')
    seed_value = list_sum(seed_input.get('value'))
    value = emission_value * economicValueShare / 100 / total_yield * seed_value
    logShouldRun(cycle, MODEL, input_term_id, True, methodTier=TIER, model_key=MODEL_KEY, emission_id=term_id)
    debugValues(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                value=value,
                coefficient=1,
                input=input_term_id)

    return _emission(term_id, value, input_term)


def _run(cycle: dict, economicValueShare: float, total_yield: float, seed_input: dict, grouped_emissions: dict):
    return [
        _run_emission(cycle, economicValueShare, total_yield, seed_input, term_id, emission_value)
        for term_id, emission_value in grouped_emissions.items()
    ]


def _map_group_emissions(group_id: str, required_emission_term_ids: list, emission_ids: list):
    lookup = download_lookup('emission.csv')
    emissions = list(filter(
        lambda id: id in required_emission_term_ids,
        find_term_ids_by(lookup, column_name('inputProductionGroupId'), group_id)
    ))
    included_emissions = list(filter(lambda v: v in emission_ids, emissions))
    missing_emissions = list(filter(lambda v: v not in emission_ids, emissions))
    return {
        'group-id': group_id,
        'is-group-in-system-boundary': group_id in required_emission_term_ids,
        'total-emissions': len(emissions),
        'included-emissions': len(included_emissions),
        'missing-emissions': '-'.join(missing_emissions),
        'has-all-emissions': len(emissions) == len(included_emissions)
    }


def _filter_emissions(cycle: dict):
    required_emission_term_ids = cycle_emissions_in_system_boundary(cycle)

    emissions = [
        {
            'emission-id': i.get('term', {}).get('@id'),
            'group-id': get_lookup_value(i.get('term', {}), LOOKUPS['emission'], model=MODEL, model_key=MODEL_KEY),
            'value': list_sum(i.get('value'))
        }
        for i in cycle.get('emissions', [])
        if all([
            i.get('term', {}).get('@id') in required_emission_term_ids,
            len(i.get('value', [])) > 0
        ])
    ]
    emission_ids = set([v.get('emission-id') for v in emissions])
    group_ids = set([v.get('group-id') for v in emissions if v.get('group-id')])

    # for each group, get the list of all required emissions
    emissions_per_group = [
        _map_group_emissions(group_id, required_emission_term_ids, emission_ids)
        for group_id in group_ids
    ]
    # only keep groups that have all emissions present in the Cycle
    valid_groups = list(filter(lambda group: all([
        group.get('has-all-emissions'),
        group.get('is-group-in-system-boundary')
    ]), emissions_per_group))
    valid_group_ids = set([v.get('group-id') for v in valid_groups])

    # finally, only return emissions which groups are valid
    return list(filter(
        lambda emission: emission.get('group-id') in valid_group_ids,
        emissions
    )), emissions_per_group


def _crop_data(product: dict, country_id: str, end_year: int):
    term = product.get('term', {})
    term_id = term.get('@id')

    crop_grouping = get_crop_lookup_value(MODEL, term_id, term_id, 'cropGroupingFaostatProduction')
    crop_grouping_proxy = get_crop_lookup_value(MODEL, term_id, term_id, 'cropGroupingFaostatProductionProxy')

    faostat_yield = safe_parse_float(extract_grouped_data_closest_date(get_region_lookup_value(
        'region-crop-cropGroupingFaostatProduction-yield.csv',
        country_id,
        crop_grouping_proxy or crop_grouping,
        model=MODEL,
        model_key=MODEL_KEY
    ), end_year), default=None)

    # when using proxy, we cannot use the lookup value as it won't correspond to the primary product
    global_evs = None if crop_grouping_proxy else safe_parse_float(
        get_lookup_value(product.get('term', {}), 'global_economic_value_share', model=MODEL, model_key=MODEL_KEY),
        default=None
    )
    product_evs = product.get('economicValueShare')

    return {
        'product-id': term_id,
        'seed-id': get_lookup_value(term, 'correspondingSeedTermIds', model=MODEL, model_key=MODEL_KEY) or None,
        'economicValueShare': global_evs or product_evs,
        'FAOSTAT-yield': faostat_yield,
        'landCover-id': get_landCover_term_id(term, model=MODEL, model_key=MODEL_KEY)
    } | (
        # skip using product yield if proxy is used
        {} if crop_grouping_proxy else {'product-yield': list_sum(product.get('value'))}
    )


def _group_seed_inputs(inputs: list):
    grouped_inputs = group_by(inputs, ['term.@id'])
    return [
        inputs[0] | {'value': flatten([v.get('value') for v in inputs])}
        for inputs in grouped_inputs.values()
    ]


def _should_run(cycle: dict):
    crop_products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    site_type_valid = valid_site_type(cycle.get('site', {}), [
        SiteSiteType.CROPLAND.value, SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
    ])
    is_product_complete = _is_term_type_complete(cycle, 'product')
    end_year = cycle_end_year(cycle)
    country_id = cycle.get('site', {}).get('country', {}).get('@id')

    # only keep the crop products that map to a seed
    crop_products = [_crop_data(product, country_id, end_year) for product in crop_products]
    valid_crop_products = [
        value for value in crop_products if all([
            value.get('seed-id'),
            value.get('economicValueShare'),
            value.get('FAOSTAT-yield') or value.get('product-yield'),
            value.get('landCover-id'),
        ])
    ]

    # array of ; delimited values
    seed_term_ids = list(set(flatten([v.get('seed-id').split(';') for v in valid_crop_products if v.get('seed-id')])))

    seed_inputs = [
        {
            'input': i,
            'is-corresponding-seed': i.get('term', {}).get('@id') in seed_term_ids,
            'input-value': list_sum(i.get('value'), default=None),
            'has-linked-impact-assessment': bool(i.get('impactAssessment')),
            'is-fromCycle': i.get('fromCycle', False),
            'is-producedInCycle': i.get('producedInCycle', False),
        }
        for i in filter_list_term_type(cycle.get('inputs', []), TermTermType.SEED)
    ]
    # sum up seed inputs with the same id
    grouped_seed_inputs = _group_seed_inputs([
        v.get('input') for v in seed_inputs
        if all([
            v.get('is-corresponding-seed', False),
            v.get('input-value') or -1 > 0,
            not v.get('has-linked-impact-assessment'),
            not v.get('is-fromCycle'),
            not v.get('is-producedInCycle'),
        ])
    ])

    crop_land_cover_ids = list(set([p.get('landCover-id') for p in valid_crop_products]))
    total_economicValueShare = list_sum([p.get('economicValueShare') for p in valid_crop_products])
    total_yield = list_sum([p.get('FAOSTAT-yield') or p.get('product-yield') for p in valid_crop_products])

    emissions, emissions_per_group = _filter_emissions(cycle)
    # group emissions with the same group-id
    grouped_emissions = reduce(
        lambda p, c: p | {c.get('group-id'): p.get(c.get('group-id'), 0) + (c.get('value') or 0)},
        emissions,
        {}
    )
    has_single_land_cover = len(crop_land_cover_ids) <= 1

    should_run = all([
        site_type_valid,
        has_single_land_cover,
        is_product_complete,
        total_economicValueShare,
        total_yield,
        bool(grouped_seed_inputs),
        bool(emissions)
    ])

    logs = {
        'site_type_valid': site_type_valid,
        'crop_products': log_as_table(crop_products),
        'crop_land_cover_ids': ';'.join(crop_land_cover_ids),
        'has_single_land_cover': has_single_land_cover,
        'is_term_type_product_complete': is_product_complete,
        'total_economicValueShare': total_economicValueShare,
        'total_yield': total_yield,
        'end_year': end_year,
        'country_id': country_id
    }

    for seed_input in seed_inputs:
        term_id = seed_input.get('input').get('term', {}).get('@id')

        logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        emissions=log_as_table(emissions),
                        emissions_per_group=log_as_table(emissions_per_group),
                        **_omit(seed_input, 'input'),
                        **logs)

        logShouldRun(cycle, MODEL, term_id, should_run, methodTier=TIER, model_key=MODEL_KEY)

        # log failed emissions to show in the logs
        for group in emissions_per_group:
            emission_id = group.get('group-id')
            if not group.get('has-all-emissions') or not should_run:
                logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY, emission_id=emission_id,
                                **group,
                                **_omit(seed_input, 'input'),
                                **logs)
                logShouldRun(cycle, MODEL, term_id, False,
                             methodTier=TIER, model_key=MODEL_KEY, emission_id=emission_id)

    return should_run, total_economicValueShare, total_yield, grouped_seed_inputs, grouped_emissions


def run(cycle: dict):
    should_run, economicValueShare, total_yield, seed_inputs, grouped_emissions = _should_run(cycle)
    return flatten(non_empty_list([
        _run(cycle, economicValueShare, total_yield, seed_input, grouped_emissions)
        for seed_input in seed_inputs
    ])) if should_run else []
