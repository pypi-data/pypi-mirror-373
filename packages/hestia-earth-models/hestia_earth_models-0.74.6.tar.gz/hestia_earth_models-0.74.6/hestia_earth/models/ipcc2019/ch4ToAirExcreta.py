from enum import Enum
from hestia_earth.schema import EmissionMethodTier, TermTermType
from hestia_earth.utils.lookup import download_lookup, get_table_value, extract_grouped_data
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float, list_sum

from hestia_earth.models.log import debugValues, logRequirements, debugMissingLookup, logShouldRun, log_as_table
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.constant import Units, DAYS_PER_MONTH
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.productivity import PRODUCTIVITY, get_productivity
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.input import total_excreta
from hestia_earth.models.utils.lookup import get_region_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.excreta": "",
        "cycleDuration": "",
        "endDate": "",
        "practices": [{"@type": "Practice", "value": "", "term.termType": "excretaManagement"}],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"},
            "measurements": [{"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}]
        }
    }
}
LOOKUPS = {
    "region": "HDI",
    "region-excreta-excretaManagement-ch4B0": "",
    "excretaManagement-ecoClimateZone-CH4conv": ""
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
TERM_ID = 'ch4ToAirExcreta'
TIER = EmissionMethodTier.TIER_2.value


class DURATION(Enum):
    MONTH_1 = '1_month'
    MONTH_3 = '3_months'
    MONTH_4 = '4_months'
    MONTH_6 = '6_months'
    MONTH_12 = '12_months'


# defaults to 12 months when no duration data provided
DEFAULT_DURATION = DURATION.MONTH_12
DURATION_KEY = {
    DURATION.MONTH_1: lambda duration: duration <= 1 * DAYS_PER_MONTH,
    DURATION.MONTH_3: lambda duration: duration <= 3 * DAYS_PER_MONTH,
    DURATION.MONTH_4: lambda duration: duration <= 4 * DAYS_PER_MONTH,
    DURATION.MONTH_6: lambda duration: duration <= 6 * DAYS_PER_MONTH,
    DEFAULT_DURATION: lambda _duration: True
}


def _get_duration_key(duration: int):
    # returns the first matching duration interval from the key
    return next((key for key in DURATION_KEY if duration and DURATION_KEY[key](duration)), DEFAULT_DURATION)


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(excreta_b0_product: float, ch4_conv_factor: float):
    value = excreta_b0_product * 0.67 * ch4_conv_factor / 100
    return [_emission(value)]


def _get_excreta_b0(country: dict, input: dict):
    # lookup data is stored as high or low productivity, and data where there is neither
    # a high or low value is stored in the lookup as "high"
    # therefore this model defaults to "high" productivity in these cases to ascertain this value
    productivity_key = get_productivity(country)
    term_id = input.get('term', {}).get('@id')
    lookup_name = 'region-excreta-excretaManagement-ch4B0.csv'
    data_values = get_region_lookup_value(lookup_name, country.get('@id'), term_id, model=MODEL, term=TERM_ID)
    return safe_parse_float(
        extract_grouped_data(data_values, productivity_key.value) or
        extract_grouped_data(data_values, PRODUCTIVITY.HIGH.value),  # defaults to high if low is not found
        default=None
    )


def _get_excretaManagement_MCF_from_lookup(term_id: str, ecoClimateZone: int, duration_key: DURATION):
    lookup_name = 'excretaManagement-ecoClimateZone-CH4conv.csv'
    lookup = download_lookup(lookup_name)
    data_values = get_table_value(lookup, 'termid', term_id, str(ecoClimateZone))
    debugMissingLookup(lookup_name, 'termid', term_id, ecoClimateZone, data_values, model=MODEL, term=TERM_ID)
    return safe_parse_float(
        extract_grouped_data(data_values, duration_key.value)
        or extract_grouped_data(data_values, DEFAULT_DURATION.value),  # defaults to 12 months if no duration specified
        default=None
    ) if data_values else 0


def _get_ch4_conv_factor(cycle: dict):
    duration = cycle.get('cycleDuration')  # uses `transformationDuration` for a `Transformation`
    duration_key = _get_duration_key(duration)
    end_date = cycle.get('endDate')
    measurements = cycle.get('site', {}).get('measurements', [])
    ecoClimateZone = most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.EXCRETAMANAGEMENT)
    practice_id = practices[0].get('term', {}).get('@id') if len(practices) > 0 else None

    debugValues(cycle, model=MODEL, term=TERM_ID,
                duration=duration_key.value,
                ecoClimateZone=ecoClimateZone,
                practice_id=practice_id)

    return _get_excretaManagement_MCF_from_lookup(practice_id, ecoClimateZone, duration_key) if practice_id else 0


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    excreta_complete = _is_term_type_complete(cycle, TermTermType.EXCRETA)
    # total of excreta including the CH4 factor
    excreta = filter_list_term_type(cycle.get('inputs', []), TermTermType.EXCRETA)
    excreta = _filter_list_term_unit(excreta, Units.KG_VS)
    excreta_values = [
        (i.get('term', {}).get('@id'), total_excreta([i], Units.KG_VS), _get_excreta_b0(country, i)) for i in excreta
    ]
    excreta_logs = log_as_table([
        {'id': id, 'value': v, 'b0': b0} for id, v, b0 in excreta_values
    ])
    excreta_b0_product = list_sum([v * f for id, v, f in excreta_values if v is not None and f is not None])

    ch4_conv_factor = _get_ch4_conv_factor(cycle)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_excreta_complete=excreta_complete,
                    excreta=excreta_logs,
                    ch4_conv_factor=ch4_conv_factor,
                    country=country.get('@id'))

    should_run = excreta_complete or all([excreta_b0_product, ch4_conv_factor])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, excreta_b0_product, ch4_conv_factor


def run(cycle: dict):
    should_run, excreta_b0_product, ch4_conv_factor = _should_run(cycle)
    return _run(excreta_b0_product, ch4_conv_factor) if should_run else []
