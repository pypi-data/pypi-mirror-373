from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import sum_values, multiply_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import (
    convert_value_from_cycle, get_product, get_site
)
from hestia_earth.models.utils.input import sum_input_impacts
from .utils import get_region_factor
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "siteType": "",
            "or": {
                "ecoregion": "",
                "country": {"@type": "Term", "termType": "region"}
            }
        },
        "cycle": {
            "@type": "Cycle",
            "products": [{
                "@type": "Product",
                "primary": "True",
                "value": "> 0",
                "economicValueShare": "> 0"
            }]
        },
        "optional": {
            "emissionsResourceUse": [
                {"@type": "Indicator", "value": "", "term.@id": "landTransformation20YearAverageDuringCycle"}
            ]
        }
    }
}
RETURNS = {
    "Indicator": {
        "value": ""
    }
}
LOOKUPS = {
    "@doc": "Different lookup files are used depending on the situation",
    "ecoregion-siteType-LandTransformationChaudaryBrooks2018CF": "",
    "region-siteType-LandTransformationChaudaryBrooks2018CF": ""
}
TERM_ID = 'damageToTerrestrialEcosystemsLandTransformation'

_LOOKUP_SUFFIX = 'LandTransformationChaudaryBrooks2018CF'
_TRANSFORMATION_TERM_ID = 'landTransformation20YearAverageDuringCycle'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def _run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    landTransformation = find_term_match(impact_assessment.get('emissionsResourceUse', []), _TRANSFORMATION_TERM_ID)
    debugValues(impact_assessment, model=MODEL, term=TERM_ID,
                node=_TRANSFORMATION_TERM_ID,
                value=landTransformation.get('value'),
                coefficient=1)

    region_factor = get_region_factor(
        TERM_ID, impact_assessment, _LOOKUP_SUFFIX, 'medium_intensity', blank_node=landTransformation
    )
    inputs_value = convert_value_from_cycle(
        impact_assessment, product, sum_input_impacts(cycle.get('inputs', []), TERM_ID), model=MODEL, term_id=TERM_ID
    )
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    landTransformation=landTransformation.get('value'),
                    region_factor=region_factor,
                    inputs_value=inputs_value)
    value = sum_values([
        multiply_values([landTransformation.get('value'), region_factor]),
        inputs_value
    ])
    return _indicator(value) if value is not None else None


def _should_run(impact_assessment: dict):
    site = get_site(impact_assessment)
    # does not run without a site as data is geospatial
    should_run = all([site])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run


def run(impact_assessment: dict):
    return _run(impact_assessment) if _should_run(impact_assessment) else None
