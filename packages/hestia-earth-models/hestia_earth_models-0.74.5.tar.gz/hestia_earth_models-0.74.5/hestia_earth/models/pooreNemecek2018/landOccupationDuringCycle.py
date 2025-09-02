from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product, get_site
from hestia_earth.models.utils.cycle import land_occupation_per_kg
from hestia_earth.models.utils.site import get_land_cover_term_id as get_landCover_term_id_from_site_type
from hestia_earth.models.utils.crop import get_landCover_term_id
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "product": {
            "@type": "Term",
            "economicValueShare": "> 0",
            "value": "> 0"
        },
        "cycle": {
            "@type": "Cycle",
            "or": [
                {
                    "@doc": "if the [cycle.functionalUnit](https://hestia.earth/schema/Cycle#functionalUnit) = 1 ha, additional properties are required",  # noqa: E501
                    "cycleDuration": "",
                    "practices": [{"@type": "Practice", "value": "", "term.@id": "longFallowRatio"}]
                },
                {
                    "@doc": "for plantations, additional properties are required",
                    "practices": [
                        {"@type": "Practice", "value": "", "term.@id": "nurseryDensity"},
                        {"@type": "Practice", "value": "", "term.@id": "nurseryDuration"},
                        {"@type": "Practice", "value": "", "term.@id": "plantationProductiveLifespan"},
                        {"@type": "Practice", "value": "", "term.@id": "plantationDensity"},
                        {"@type": "Practice", "value": "", "term.@id": "plantationLifespan"},
                        {"@type": "Practice", "value": "", "term.@id": "rotationDuration"}
                    ]
                }
            ]
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "landCover": ""
    }]
}
TERM_ID = 'landOccupationDuringCycle'


def _indicator(term_id: str, value: float, land_cover_term_id: str):
    indicator = _new_indicator(term_id, MODEL, land_cover_term_id)
    indicator['value'] = value
    return indicator


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment)
    product_evs = product.get('economicValueShare')
    cycle = impact_assessment.get('cycle', {})
    site = get_site(impact_assessment)
    land_cover_from_product = get_landCover_term_id(product.get('term', {}))
    land_cover_from_site = get_landCover_term_id_from_site_type(site.get('siteType'))
    land_cover_term_id = land_cover_from_product or land_cover_from_site
    land_occupation_m2_kg = land_occupation_per_kg(MODEL, TERM_ID, cycle, site, product)

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    economicValueShare=product_evs,
                    land_occupation_kg=land_occupation_m2_kg,
                    land_cover_from_product=land_cover_from_product,
                    land_cover_from_site=land_cover_from_site)

    should_run = all([product_evs, land_cover_term_id, land_occupation_m2_kg is not None])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, land_occupation_m2_kg, land_cover_term_id


def run(impact_assessment: dict):
    should_run, land_occupation_kg, land_cover_term_id = _should_run(impact_assessment)
    return [_indicator(TERM_ID, land_occupation_kg, land_cover_term_id)] if should_run else []
