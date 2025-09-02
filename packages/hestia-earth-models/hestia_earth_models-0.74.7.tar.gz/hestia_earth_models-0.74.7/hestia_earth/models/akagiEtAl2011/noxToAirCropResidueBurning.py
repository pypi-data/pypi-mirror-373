from hestia_earth.schema import EmissionMethodTier

from .utils import run_emission

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "products": [{
                "@type": "Product",
                "term.@id": ["aboveGroundCropResidueBurnt", "discardedCropBurnt"],
                "value": ""
            }],
            "completeness.cropResidue": "True"
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "emission": ["akagiEtAl2011CropResidueBurningFactor", "akagiEtAl2011CropResidueBurningFactor-sd"]
}
TERM_ID = 'noxToAirCropResidueBurning'
TIER = EmissionMethodTier.TIER_1.value


def run(cycle: dict): return run_emission(TERM_ID, cycle)
