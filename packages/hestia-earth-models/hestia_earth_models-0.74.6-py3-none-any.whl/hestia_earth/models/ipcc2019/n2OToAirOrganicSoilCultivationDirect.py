from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import land_occupation_per_ha
from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone, get_eco_climate_zone_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.site import valid_site_type

from .organicSoilCultivation_utils import (
    assign_organic_soil_category, calc_emission, format_number, get_emission_factor, OrganicSoilCategory,
    remap_categories, valid_eco_climate_zone
)
from . import MODEL


REQUIREMENTS = {
    "Cycle": {
        "or": [
            {
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
        ],
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "histosol"},
                {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
            ]
        },
        "optional": {
            "cycleDuration": ""
        }
    }
}
LOOKUPS = {
    "crop": [
        "isPlantation",
        "IPCC_2013_ORGANIC_SOIL_CULTIVATION_CATEGORY"
    ],
    "forage": [
        "isPlantation",
        "IPCC_2013_ORGANIC_SOIL_CULTIVATION_CATEGORY"
    ],
    "ecoClimateZone": [
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_ANNUAL_CROPS",
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_PERENNIAL_CROPS",
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_ACACIA",
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_OIL_PALM",
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_SAGO_PALM",
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_PADDY_RICE_CULTIVATION",
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_GRASSLAND",
        "IPCC_2013_ORGANIC_SOILS_TONNES_N2O-N_HECTARE_OTHER"
    ]
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "statsDefinition": "modelled",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'n2OToAirOrganicSoilCultivationDirect'
TIER = EmissionMethodTier.TIER_1.value

_STATS_DEFINITION = EmissionStatsDefinition.MODELLED.value

_CATEGORY_REMAPPER = {
    OrganicSoilCategory.ACACIA: OrganicSoilCategory.PERENNIAL_CROPS
}


def _emission(value: float, sd: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['sd'] = [sd]
    emission['statsDefinition'] = _STATS_DEFINITION
    emission['methodTier'] = TIER
    return emission


def sample_emission_factor(
    eco_climate_zone: EcoClimateZone,
    organic_soil_category: OrganicSoilCategory,
) -> tuple[float, float]:
    category = remap_categories(organic_soil_category, _CATEGORY_REMAPPER)  # fewer categories than CO2 model
    factor_data = get_emission_factor(TERM_ID, eco_climate_zone, category)
    mean = factor_data.get("value", 0)
    sd = factor_data.get("sd", 0)
    return mean, sd


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])

    def _get_measurement_content(term_id: str):
        return most_relevant_measurement_value(measurements, term_id, end_date)

    histosol = _get_measurement_content('histosol')
    eco_climate_zone = get_eco_climate_zone_value(cycle, as_enum=True)
    organic_soil_category = assign_organic_soil_category(cycle, log_id=TERM_ID)

    emission_factor_mean, emission_factor_sd = (
        sample_emission_factor(eco_climate_zone, organic_soil_category)
        if eco_climate_zone
        else (None, None)
    )

    land_occupation = land_occupation_per_ha(MODEL, TERM_ID, cycle)

    logRequirements(
        cycle, model=MODEL, term=TERM_ID,
        eco_climate_zone=eco_climate_zone,
        organic_soil_category=organic_soil_category,
        emission_factor=f"{format_number(emission_factor_mean)} ± {format_number(emission_factor_sd)}",
        land_occupation=format_number(land_occupation),
        histosol=format_number(histosol)
    )

    should_run = all([
        valid_site_type(site),
        valid_eco_climate_zone(eco_climate_zone),
        all(
            var is not None for var in [
                emission_factor_mean,
                emission_factor_sd,
                land_occupation,
                histosol
            ]
        )
    ])

    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)

    return should_run, emission_factor_mean, emission_factor_sd, histosol, land_occupation


def _run(emission_factor_mean: float, emission_factor_sd: float, histosol: float, land_occupation: float):
    value = round(calc_emission(TERM_ID, emission_factor_mean, histosol, land_occupation), 6)
    sd = round(calc_emission(TERM_ID, emission_factor_sd, histosol, land_occupation), 6)
    return [_emission(value, sd)]


def run(cycle: dict):
    should_run, emission_factor_mean, emission_factor_sd, histosol, land_occupation = _should_run(cycle)
    return _run(emission_factor_mean, emission_factor_sd, histosol, land_occupation) if should_run else []
