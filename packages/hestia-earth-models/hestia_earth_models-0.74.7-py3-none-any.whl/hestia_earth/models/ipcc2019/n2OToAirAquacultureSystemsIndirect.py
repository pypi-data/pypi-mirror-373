from hestia_earth.schema import EmissionMethodTier

from .n2OToAir_indirect_emissions_utils import run as run_emission

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "True",
        "emissions": [
            {"@type": "Emission", "value": "", "term.@id": "nh3ToSurfaceWaterAquacultureSystems"},
            {"@type": "Emission", "value": "", "term.@id": "nh3ToAirAquacultureSystems"},
            {"@type": "Emission", "value": "", "term.@id": "noxToAirAquacultureSystems"}
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
TERM_ID = 'n2OToAirAquacultureSystemsIndirect'
TIER = EmissionMethodTier.TIER_1.value
_NO3_TERM_ID = 'nh3ToSurfaceWaterAquacultureSystems'
_NH3_TERM_ID = 'nh3ToAirAquacultureSystems'
_NOX_TERM_ID = 'noxToAirAquacultureSystems'
_EMISSION_IDS = [_NH3_TERM_ID, _NO3_TERM_ID, _NOX_TERM_ID]


def run(cycle: dict):
    return run_emission(TERM_ID, _EMISSION_IDS, cycle)
