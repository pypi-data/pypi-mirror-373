from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value, extract_grouped_data
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugMissingLookup, debugValues, logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.blank_node import get_total_value_converted_with_min_ratio
from hestia_earth.models.utils.term import get_ionophore_terms
from hestia_earth.models.utils.input import get_feed_inputs
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.liveAnimal import get_default_digestibility
from .utils import get_milkYield_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "True",
        "completeness.freshForage": "True",
        "or": [
            {
                "animals": [{
                    "@type": "Animal",
                    "inputs": [{
                        "@type": "Input",
                        "term.units": "kg",
                        "value": "> 0",
                        "optional": {
                            "properties": [{
                                "@type": "Property",
                                "value": "",
                                "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                            }]
                        }
                    }]
                }]
            },
            {
                "inputs": [{
                    "@type": "Input",
                    "term.units": "kg",
                    "value": "> 0",
                    "isAnimalFeed": "True",
                    "optional": {
                        "properties": [{
                            "@type": "Property",
                            "value": "",
                            "term.@id": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
                        }]
                    }
                }]
            }
        ],
        "optional": {
            "inputs": [{"@type": "Input", "term.@id": ["ionophores", "ionophoreAntibiotics"]}]
        }
    }
}
LOOKUPS = {
    "animalProduct": [
        "digestibility",
        "percentageYmMethaneConversionFactorEntericFermentation",
        "percentageYmMethaneConversionFactorEntericFermentation-sd",
        "defaultPercentageYmMethaneConversionFactorEntericFermentation",
        "defaultPercentageYmMethaneConversionFactorEntericFermentation-min",
        "defaultPercentageYmMethaneConversionFactorEntericFermentation-max"
    ],
    "liveAnimal": [
        "digestibility",
        "percentageYmMethaneConversionFactorEntericFermentation",
        "percentageYmMethaneConversionFactorEntericFermentation-sd",
        "defaultPercentageYmMethaneConversionFactorEntericFermentation",
        "defaultPercentageYmMethaneConversionFactorEntericFermentation-min",
        "defaultPercentageYmMethaneConversionFactorEntericFermentation-max"
    ],
    "crop-property": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"],
    "forage-property": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"],
    "processedFood-property": ["neutralDetergentFibreContent", "energyContentHigherHeatingValue"]
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "methodTier": "tier 2",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'ch4ToAirEntericFermentation'
TIER = EmissionMethodTier.TIER_2.value
METHANE_EC = 55.65  # MJ/kg CH4


def _emission(value: float, sd: float = None, min: float = None, max: float = None, description: str = None):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    if sd is not None:
        emission['sd'] = [sd]
        emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    if min is not None:
        emission['min'] = [min]
        emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    if max is not None:
        emission['max'] = [max]
        emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    if description:
        emission['description'] = description
    emission['methodTier'] = TIER
    return emission


def _run(feed: float, enteric_factor: float = None, enteric_sd: float = None, default_values: dict = {}):
    default_value = default_values.get('value')
    value = (feed * ((enteric_factor or default_value) / 100)) / METHANE_EC
    min = (feed * (default_values.get('min') / 100)) / METHANE_EC if all([
        enteric_factor is None, default_values.get('min')
    ]) else None
    max = (feed * (default_values.get('max') / 100)) / METHANE_EC if all([
        enteric_factor is None, default_values.get('max')
    ]) else None
    description = f"Average Ym factor of {default_value}% used as data missing to differentiate Ym." if all([
        enteric_factor is None,
        default_value is not None
    ]) else None
    return [
        _emission(value, enteric_sd, min, max, description)
    ]


DE_NDF_MAPPING = {
    'high_DE_low_NDF': lambda DE, NDF: DE >= 70 and NDF < 35,
    'high_DE_high_NDF': lambda DE, NDF: DE >= 70 and NDF >= 35,
    'medium_DE_high_NDF': lambda DE, NDF: 63 <= DE < 70 and NDF > 37,
    'low_DE_high_NDF': lambda DE, NDF: DE < 63 and NDF > 38
}
MILK_YIELD_MAPPING = {
    'high_DE_low_NDF': lambda milk_yield: milk_yield > 8500,
    'high_DE_high_NDF': lambda milk_yield: milk_yield > 8500,
    'medium_DE_high_NDF': lambda milk_yield: 5000 <= milk_yield <= 8500,
    'low_DE_high_NDF': lambda milk_yield: 0 < milk_yield < 5000
}

DE_MAPPING = {
    'high_medium_DE': lambda DE, _: DE > 62,
    'medium_DE': lambda DE, _: DE > 62 and DE < 72,
    'low_DE': lambda DE, _: DE <= 62,
    'high_DE': lambda DE, _: DE >= 72,
    'high_DE_ionophore': lambda DE, ionophore: DE >= 75 and ionophore
}


def _get_grouped_data_key(keys: list, DE: float, NDF: float, ionophore: bool, milk_yield: float):
    # test conditions one by one and return the key associated for the first one that passes
    return (
        (next(
            (key for key in keys if key in DE_NDF_MAPPING and DE_NDF_MAPPING[key](DE, NDF)),
            None
        ) if all([DE is not None, NDF is not None]) else None) or next(
            (key for key in keys if key in DE_MAPPING and DE_MAPPING[key](DE, ionophore)),
            None
        ) if DE else None
    ) or (
        next(
            (key for key in keys if key in MILK_YIELD_MAPPING and MILK_YIELD_MAPPING[key](milk_yield)),
            None
        ) if milk_yield else None
    )


def _extract_groupped_data(value: str, DE: float, NDF: float, ionophore: bool, milk_yield: float):
    value_keys = [val.split(':')[0] for val in value.split(';')]
    value_key = _get_grouped_data_key(value_keys, DE, NDF, ionophore, milk_yield)

    debugValues({}, model=MODEL, term=TERM_ID,
                value_key=value_key)

    return safe_parse_float(extract_grouped_data(value, value_key), default=None)


def _get_lookup_value(lookup, term: dict, lookup_col: str, DE: float, NDF: float, ionophore: bool, milk_yield: float):
    term_id = term.get('@id')
    value = get_table_value(lookup, 'termid', term_id, column_name(lookup_col)) if term_id else None
    debugMissingLookup(f"{term.get('termType')}.csv", 'termid', term_id, lookup_col, value, model=MODEL, term=TERM_ID)
    return value if value is None or ':' not in value else _extract_groupped_data(value, DE, NDF, ionophore, milk_yield)


def _get_milk_yield(cycle: dict):
    value = list_sum(get_milkYield_practice(cycle).get('value', []), 0)
    return value * cycle.get('cycleDuration', 365) if value > 0 else None


def _get_DE_type(lookup, term_id: str, term_type: str):
    lookup_col = LOOKUPS.get(term_type, [None])[0]
    value = get_table_value(lookup, 'termid', term_id, column_name(lookup_col)) if lookup_col else None
    debugMissingLookup(f"{term_type}.csv", 'termid', term_id, lookup_col, value, model=MODEL, term=TERM_ID)
    return value


def _is_ionophore(cycle: dict, total_feed: float):
    inputs = cycle.get('inputs', [])
    ionophore_terms = get_ionophore_terms()
    has_input = any([find_term_match(inputs, term_id, None) is not None for term_id in ionophore_terms])
    maize_input = find_term_match(inputs, 'maizeSteamFlaked')
    maize_feed = get_total_value_converted_with_min_ratio(MODEL, None, blank_nodes=[maize_input]) if maize_input else 0
    maize_feed_ratio = maize_feed / total_feed if all([maize_feed, total_feed]) else 0

    debugValues(cycle, model=MODEL, term=TERM_ID,
                maize_feed_in_MJ=maize_feed,
                maize_feed_ratio=maize_feed_ratio)

    return has_input and maize_feed_ratio >= 0.9


def _get_default_values(lookup, term: dict):
    term_id = term.get('@id')
    value = get_table_value(lookup, 'termid', term_id, column_name(LOOKUPS['liveAnimal'][3])) if term_id else None
    min = get_table_value(lookup, 'termid', term_id, column_name(LOOKUPS['liveAnimal'][4])) if term_id else None
    max = get_table_value(lookup, 'termid', term_id, column_name(LOOKUPS['liveAnimal'][5])) if term_id else None
    return {
        'value': safe_parse_float(value, default=None),
        'min': safe_parse_float(min, default=None),
        'max': safe_parse_float(max, default=None)
    }


def _should_run(cycle: dict):
    is_animalFeed_complete = cycle.get('completeness', {}).get('animalFeed', False) is True
    is_freshForage_complete = cycle.get('completeness', {}).get('freshForage', False) is True

    primary_product = find_primary_product(cycle) or {}
    term = primary_product.get('term', {})
    term_id = term.get('@id')
    term_type = term.get('termType')
    lookup_name = f"{term_type}.csv"
    lookup = download_lookup(lookup_name)

    DE_type = _get_DE_type(lookup, term_id, term_type) if term_id else None

    feed_inputs = get_feed_inputs(cycle)

    total_feed = get_total_value_converted_with_min_ratio(MODEL, TERM_ID, cycle, feed_inputs)
    ionophore = _is_ionophore(cycle, total_feed) if total_feed else False
    milk_yield = _get_milk_yield(cycle)

    # only keep inputs that have a positive value
    inputs = list(filter(lambda i: list_sum(i.get('value', [])) > 0, feed_inputs))
    DE = get_total_value_converted_with_min_ratio(
        MODEL, TERM_ID, cycle, inputs, prop_id=DE_type, is_sum=False
    ) if DE_type else None
    # set as a percentage in the properties
    DE = DE * 100 if DE else DE
    DE_default = get_default_digestibility(MODEL, TERM_ID, cycle)

    # set as a percentage in the properties
    NDF = get_total_value_converted_with_min_ratio(
        MODEL, TERM_ID, cycle, inputs, prop_id='neutralDetergentFibreContent', is_sum=False
    )
    NDF = NDF * 100 if NDF else NDF

    enteric_factor = safe_parse_float(_get_lookup_value(
        lookup, term, LOOKUPS['liveAnimal'][1], DE or DE_default, NDF, ionophore, milk_yield
    ), default=None)
    enteric_sd = safe_parse_float(_get_lookup_value(
        lookup, term, LOOKUPS['liveAnimal'][2], DE or DE_default, NDF, ionophore, milk_yield
    ), default=None)

    default_values = _get_default_values(lookup, term)

    debugValues(cycle, model=MODEL, term=TERM_ID,
                DE_type=DE_type,
                DE=DE,
                **({'DE_default_lookup': DE_default} if not DE else {}),
                NDF=NDF,
                ionophore=ionophore,
                milk_yield=milk_yield,
                enteric_factor=enteric_factor,
                enteric_sd=enteric_sd,
                default_values=log_as_table(default_values))

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_animalFeed_complete=is_animalFeed_complete,
                    term_type_freshForage_complete=is_freshForage_complete,
                    total_feed_in_MJ=total_feed)

    should_run = all([
        is_animalFeed_complete, is_freshForage_complete, total_feed,
        enteric_factor or default_values.get('value')
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, total_feed, enteric_factor, enteric_sd, default_values


def run(cycle: dict):
    should_run, feed, enteric_factor, enteric_sd, default_values = _should_run(cycle)
    return _run(feed, enteric_factor, enteric_sd, default_values) if should_run else []
