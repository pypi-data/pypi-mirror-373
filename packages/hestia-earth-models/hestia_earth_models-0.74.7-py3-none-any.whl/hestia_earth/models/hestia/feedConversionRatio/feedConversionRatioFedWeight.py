from hestia_earth.utils.tools import list_sum

from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.input import get_feed_inputs

REQUIREMENTS = {
    "Cycle": {
        "or": [
            {
                "animals": [{
                    "@type": "Animal",
                    "inputs": [{
                        "@type": "Input",
                        "term.units": "kg",
                        "value": "> 0",
                        "properties": [
                            {"@type": "Property", "value": "", "term.@id": "energyContentHigherHeatingValue"}
                        ]
                    }]
                }]
            },
            {
                "inputs": [{
                    "@type": "Input",
                    "term.units": "kg",
                    "value": "> 0",
                    "isAnimalFeed": "True",
                    "properties": [
                        {"@type": "Property", "value": "", "term.@id": "energyContentHigherHeatingValue"}
                    ]
                }]
            }
        ],
        "products": [{
            "@type": "Product",
            "term.termType": "animalProduct",
            "properties": [{
                "@type": "Property",
                "value": "",
                "term.@id": "liveweightPerHead"
            }],
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": [
                        "processingConversionLiveweightToColdCarcassWeight",
                        "processingConversionLiveweightToColdDressedCarcassWeight",
                        "processingConversionColdCarcassWeightToReadyToCookWeight",
                        "processingConversionColdDressedCarcassWeightToReadyToCookWeight"
                    ]
                }]
            }
        }]
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'feedConversionRatioFedWeight'


def run(cycle: dict, feed: float):
    return list_sum(get_total_value(get_feed_inputs(cycle)))
