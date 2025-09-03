from hestia_earth.utils.tools import list_sum

from hestia_earth.models.utils.blank_node import get_total_value_converted
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
                            {"@type": "Property", "value": "", "term.@id": "energyContentHigherHeatingValue"},
                            {"@type": "Property", "value": "", "term.@id": "dryMatter"}
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
                    "optional": {
                        "properties": [{
                            "@type": "Property",
                            "value": "",
                            "term.@id": ["energyContentHigherHeatingValue"]
                        }]
                    }
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
TERM_ID = 'feedConversionRatioDryMatter'


def run(cycle: dict, feed: float):
    return list_sum(get_total_value_converted(get_feed_inputs(cycle), 'dryMatter'))
