from hestia_earth.schema import EmissionMethodTier

from .n2OToAir_indirect_emissions_utils import run as run_emission

REQUIREMENTS = {
    "Cycle": {
        "emissions": [
            {"@type": "Emission", "value": "", "term.@id": "no3ToGroundwaterOrganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "nh3ToAirOrganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "noxToAirOrganicFertiliser"}
        ],
        "optional": {
            "site": {
                "@type": "Site",
                "measurements": [
                    {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
                ]
            }
        }
    }
}
LOOKUPS = {
    "emission": [
        "IPCC_2019_EF4_FACTORS", "IPCC_2019_EF4_FACTORS-max", "IPCC_2019_EF4_FACTORS-min",
        "IPCC_2019_EF5_FACTORS", "IPCC_2019_EF5_FACTORS-max", "IPCC_2019_EF5_FACTORS-min"
    ]
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'n2OToAirOrganicFertiliserIndirect'
TIER = EmissionMethodTier.TIER_1.value
_NO3_TERM_ID = 'no3ToGroundwaterOrganicFertiliser'
_NH3_TERM_ID = 'nh3ToAirOrganicFertiliser'
_NOX_TERM_ID = 'noxToAirOrganicFertiliser'
_EMISSION_IDS = [_NH3_TERM_ID, _NO3_TERM_ID, _NOX_TERM_ID]


def run(cycle: dict):
    return run_emission(TERM_ID, _EMISSION_IDS, cycle)
