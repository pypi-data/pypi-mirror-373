from functools import reduce
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table, debugValues
from hestia_earth.models.utils import multiply_values
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.product import has_flooded_rice
from hestia_earth.models.utils.organicFertiliser import get_cycle_inputs as get_organicFertiliser_inputs
from hestia_earth.models.utils.lookup import get_region_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "practices": [
            {"@type": "Practice", "value": "", "term.@id": "croppingDuration"},
            {"@type": "Practice", "value": "", "term.termType": ["landUseManagement", "waterRegime"]},
            {"@type": "Practice", "value": "", "term.termType": "cropResidueManagement"}
        ],
        "products": [{"@type": "Product", "value": "", "term.@id": "aboveGroundCropResidueIncorporated"}],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        },
        "optional": {
            "inputs": [
                {"@type": "Input", "value": "", "term.termType": "organicFertiliser"},
                {
                    "@type": "Input",
                    "value": "",
                    "term.termType": "fertiliserBrandName",
                    "properties": [{"@type": "Property", "value": "", "key.termType": "organicFertiliser"}]
                }
            ]
        }
    }
}
LOOKUPS = {
    "landUseManagement": [
        "IPCC_2019_CH4_rice_SFp",
        "IPCC_2019_CH4_rice_SFp-min",
        "IPCC_2019_CH4_rice_SFp-max",
        "IPCC_2019_CH4_rice_SFp-sd"
    ],
    "waterRegime": [
        "IPCC_2019_CH4_rice_SFw",
        "IPCC_2019_CH4_rice_SFw-min",
        "IPCC_2019_CH4_rice_SFw-max",
        "IPCC_2019_CH4_rice_SFw-sd"
    ],
    "organicFertiliser": [
        "IPCC_2019_CH4_rice_CFOA_kg_fresh_weight",
        "IPCC_2019_CH4_rice_CFOA_kg_fresh_weight_min",
        "IPCC_2019_CH4_rice_CFOA_kg_fresh_weight_max",
        "IPCC_2019_CH4_rice_CFOA_kg_fresh_weight_sd"
    ],
    "cropResidueManagement": [
        "IPCC_2019_CH4_rice_CFOA_kg_dry_weight",
        "IPCC_2019_CH4_rice_CFOA_kg_dry_weight_min",
        "IPCC_2019_CH4_rice_CFOA_kg_dry_weight_max",
        "IPCC_2019_CH4_rice_CFOA_kg_dry_weight_sd"
    ],
    "region-ch4ef-IPCC2019": ["CH4_ef", "CH4_ef_min", "CH4_ef_max", "CH4_ef_sd"]
}
RETURNS = {
    "Emission": [{
        "value": "",
        "min": "",
        "max": "",
        "sd": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'ch4ToAirFloodedRice'
TIER = EmissionMethodTier.TIER_1.value
_STATS = ['value', 'min', 'max', 'sd']


def _emission(value: float, min: float, max: float, sd: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    if min is not None:
        emission['min'] = [min]
    if max is not None:
        emission['max'] = [max]
    if sd is not None:
        emission['sd'] = [sd]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _get_CH4_ef(country: str, suffix: str = 'value'):
    lookup_name = 'region-ch4ef-IPCC2019.csv'
    lookup = 'CH4_ef'
    lookup = '_'.join([lookup, suffix]) if suffix != 'value' else lookup
    return safe_parse_float(
        get_region_lookup_value(lookup_name, country, lookup, model=MODEL, term=TERM_ID),
        default=None
    )


def _get_cropResidue_value(cycle: dict, suffix: str = 'value'):
    product_id = 'aboveGroundCropResidueIncorporated'
    abgIncorporated = list_sum(
        find_term_match(cycle.get('products', []), product_id).get('value', []),
        default=None
    )
    abgManagement = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    term = abgManagement[0].get('term', {}) if len(abgManagement) > 0 else None
    lookup = 'IPCC_2019_CH4_rice_CFOA_kg_dry_weight'
    lookup = '_'.join([lookup, suffix]) if suffix != 'value' else lookup
    factor = safe_parse_float(
        get_lookup_value(term, lookup, model=MODEL, term=TERM_ID),
        default=None
    ) if term else None

    debugValues(cycle, model=MODEL, term=TERM_ID,
                **{'cropResidue_' + suffix: log_as_table({
                    'product-id': product_id,
                    'product-value': abgIncorporated,
                    'factor': factor
                })})

    return multiply_values([abgIncorporated, factor])


def _get_fertiliser_values(input: dict, suffix: str = 'value'):
    term = input.get('term', {})
    lookup = 'IPCC_2019_CH4_rice_CFOA_kg_fresh_weight'
    lookup = '_'.join([lookup, suffix]) if suffix != 'value' else lookup
    factor = safe_parse_float(
        get_lookup_value(term, lookup, model=MODEL, term=TERM_ID),
        default=None
    )
    value = list_sum(input.get('value', []))
    return {'input-id': term.get('@id'), 'input-value': value, 'factor': factor}


def _get_fertiliser_value(cycle: dict, suffix: str = 'value'):
    fertiliser_values = [_get_fertiliser_values(i, suffix) for i in get_organicFertiliser_inputs(cycle)]

    debugValues(cycle, model=MODEL, term=TERM_ID,
                **{'fertiliser_' + suffix: log_as_table(fertiliser_values)})

    valid_fertiliser_values = [
        value for value in fertiliser_values
        if all([value.get('input-value') is not None, value.get('factor') is not None])
    ]
    fert_value = list_sum([
        value.get('input-value') * value.get('factor')
        for value in valid_fertiliser_values
    ])
    return fert_value


def _calculate_SFo(cycle: dict, suffix: str = 'value'):
    cropResidue = _get_cropResidue_value(cycle, suffix)
    fertiliser = _get_fertiliser_value(cycle, suffix)
    return (1 + (fertiliser/1000) + (cropResidue/1000)) ** 0.59 if all([
        fertiliser is not None,
        cropResidue is not None
    ]) else None


def _get_practice_values(practice: dict, col: str, default=None):
    term = practice.get('term', {})
    factor = safe_parse_float(get_lookup_value(term, col, model=MODEL, term=TERM_ID), default)
    return {
        'practice-id': term.get('@id'),
        'factor': factor,
        'practice-value': list_sum(practice.get('value', []), default=default)
    } if factor is not None else None


def _calculate_SF_total(cycle: dict, practices: list, lookup: str, suffix: str = 'value', default=None):
    lookup_column = '-'.join([lookup, suffix]) if suffix != 'value' else lookup
    values = non_empty_list([_get_practice_values(p, lookup_column) for p in practices])

    debugValues(cycle, model=MODEL, term=TERM_ID,
                **{lookup_column: log_as_table(values)})

    used_values = [value for value in values if value.get('practice-value') is not None]

    # sum only values that are numbers
    return (
        list_sum([
            value.get('factor') * value.get('practice-value') for value in used_values
        ], default=None) / list_sum([
            value.get('practice-value') for value in used_values
        ])
    ) if used_values else (
        default if suffix == 'value' else None
    )


def _value_from_factors(values: list, key: str = 'value'):
    # get the value from all factors, and only run if all are provided
    all_values = [value.get(key) for value in values]
    return multiply_values(all_values) if all([v is not None for v in all_values]) else None


def _run(values: list):
    value = _value_from_factors(values, 'value')
    min = _value_from_factors(values, 'min')
    max = _value_from_factors(values, 'max')
    sd = _value_from_factors(values, 'sd')

    sd = (max-min)/4 if all([max, min]) else None

    return [_emission(value, min, max, sd)]


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {}).get('@id')

    flooded_rice = has_flooded_rice(cycle.get('products', []))
    practices = cycle.get('practices', [])

    croppingDuration = find_term_match(practices, 'croppingDuration', None)
    has_croppingDuration = croppingDuration is not None
    croppingDuration = reduce(lambda p, key: p | {
        key: list_sum(croppingDuration.get(key) or [], default=None)
    }, _STATS, {}) if has_croppingDuration else {}

    CH4_ef = reduce(lambda p, key: p | {key: _get_CH4_ef(country, key)}, _STATS, {})
    SFo = reduce(lambda p, key: p | {key: _calculate_SFo(cycle, key)}, _STATS, {})

    water_regime = filter_list_term_type(practices, TermTermType.WATERREGIME)
    SFw = reduce(lambda p, key: p | {
        key: _calculate_SF_total(cycle, water_regime, 'IPCC_2019_CH4_rice_SFw', key)
    }, _STATS, {})

    land_use_management = filter_list_term_type(practices, TermTermType.LANDUSEMANAGEMENT)
    SFp = reduce(lambda p, key: p | {
        key: _calculate_SF_total(cycle, land_use_management, 'IPCC_2019_CH4_rice_SFp', key, default=1)
    }, _STATS, {})

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_flooded_rice=flooded_rice,
                    country=country,
                    values=log_as_table([
                        {'name': 'croppingDuration'} | croppingDuration,
                        {'name': 'CH4-ef'} | CH4_ef,
                        {'name': 'SFo'} | SFo,
                        {'name': 'SFw'} | SFw,
                        {'name': 'SFp'} | SFp,
                    ]))

    should_run = all([
        flooded_rice,
        has_croppingDuration,
        country,
        CH4_ef.get('value') is not None,
        SFo.get('value') is not None,
        SFw.get('value') is not None,
        SFp.get('value') is not None,
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, [croppingDuration, CH4_ef, SFo, SFw, SFp]


def run(cycle: dict):
    should_run, values = _should_run(cycle)
    return _run(values) if should_run else []
