from hestia_earth.schema import MeasurementMethodClassification, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float, list_average, non_empty_list
from hestia_earth.utils.blank_node import group_by_keys

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.site import related_cycles
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "optional": {
            "measurements": [{
                "@type": "Measurement",
                "term.@id": ["brackishWater", "salineWater", "freshWater"],
                "value": "true"
            }],
            "related": {
                "Cycle": {
                    "@type": "Cycle",
                    "products": [{
                        "@type": "Product",
                        "primary": "True",
                        "term.termType": "liveAquaticSpecies"
                    }]
                }
            }
        }
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "startDate": "",
        "endDate": "",
        "methodClassification": "expert opinion"
    }]
}
LOOKUPS = {
    "liveAquaticSpecies": "defaultSalinity"
}
TERM_ID = 'waterSalinity'
_MEASUREMENT_TERM_IDS = ["brackishWater", "salineWater", "freshWater"]
_DEFAULT_SALINITY = {
    'freshWater': 0,
    'brackishWater': 5000,
    'salineWater': 32000
}


def _measurement(value: float, start_date: str = None, end_date: str = None):
    data = _new_measurement(TERM_ID, MODEL)
    data['value'] = [value]
    if start_date:
        data['startDate'] = start_date
    if end_date:
        data['endDate'] = end_date
    data['methodClassification'] = MeasurementMethodClassification.EXPERT_OPINION.value
    return data if value is not None else None


def _should_run_by_products(site: dict):
    cycles = related_cycles(site)
    relevant_products = [
        {
            'product-id': product.get('term', {}).get('@id'),
            'lookup-value': safe_parse_float(
                get_lookup_value(product.get('term', {}), LOOKUPS['liveAquaticSpecies']),
                default=None
            ),
            'start-date': product.get('startDate') or cycle.get('startDate'),
            'end-date': product.get('endDate') or cycle.get('endDate')
        }
        for cycle in cycles
        for product in filter_list_term_type(cycle.get('products', []), TermTermType.LIVEAQUATICSPECIES)
    ]
    has_valid_products = any([product.get('lookup-value') for product in relevant_products])

    logRequirements(site, model=MODEL, term=TERM_ID,
                    live_aquatic_products=log_as_table(relevant_products))

    should_run = all([has_valid_products])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, relevant_products


def _run_by_products(site: dict):
    should_run, values = _should_run_by_products(site)
    grouped_values = group_by_keys(values, ['start-date', 'end-date'])
    return non_empty_list([
        _measurement(
            list_average([v.get('lookup-value') for v in value if v.get('lookup-value')], default=0),
            value[0].get('start-date'),
            value[0].get('end-date')
        )
        for value in grouped_values.values()
    ]) if should_run else []


def _should_run_by_measurement(site: dict):
    measurements = [
        m for m in site.get('measurements', [])
        if all([
            m.get('term', {}).get('@id') in _MEASUREMENT_TERM_IDS,
            not is_from_model(m),
            m.get('value')
        ])
    ]

    logRequirements(site, model=MODEL, term=TERM_ID,
                    existing_measurements=';'.join([m.get('term', {}).get('@id') for m in measurements]))

    should_run = all([measurements])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, measurements


def _run_by_measurement(site: dict):
    should_run, measurements = _should_run_by_measurement(site)
    return [
        _measurement(_DEFAULT_SALINITY[m.get('term', {}).get('@id')], m.get('startDate'), m.get('endDate'))
        for m in measurements
    ] if should_run else []


def run(site: dict):
    return _run_by_measurement(site) or _run_by_products(site)
