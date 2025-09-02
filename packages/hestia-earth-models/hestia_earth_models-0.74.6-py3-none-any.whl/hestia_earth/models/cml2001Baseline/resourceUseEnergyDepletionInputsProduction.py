from hestia_earth.models.linkedImpactAssessment.utils import run_inputs_production
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "product": {"@type": "Term"},
        "cycle": {
            "@type": "Cycle",
            "products": [{
                "@type": "Product",
                "primary": "True",
                "value": "> 0",
                "economicValueShare": "> 0"
            }],
            "inputs": [{
                "@type": "Input",
                "impactAssessment": {
                    "@type": "ImpactAssessment",
                    "emissionsResourceUse": [{
                        "@type": "Indicator",
                        "term.@id": [
                            "resourceUseEnergyDepletionDuringCycle",
                            "resourceUseEnergyDepletionInputsProduction"
                        ],
                        "value": "> 0"
                    }]
                }
            }]
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "inputs": "units in MJ"
    }]
}
TERM_ID = 'resourceUseEnergyDepletionInputsProduction'


def run(impact_assessment: dict): return run_inputs_production(impact_assessment, TERM_ID, MODEL)
