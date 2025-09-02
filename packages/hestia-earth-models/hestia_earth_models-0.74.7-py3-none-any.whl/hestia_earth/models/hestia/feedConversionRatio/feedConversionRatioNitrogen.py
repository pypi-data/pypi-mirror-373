from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.utils.property import get_node_property_value_converted
from hestia_earth.models.utils.input import get_feed_inputs

from .. import MODEL

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
                            {"@type": "Property", "value": "", "term.@id": "crudeProteinContent"}
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
                        {"@type": "Property", "value": "", "term.@id": "energyContentHigherHeatingValue"},
                        {"@type": "Property", "value": "", "term.@id": "crudeProteinContent"}
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
LOOKUPS = {
    "crop-property": "crudeProteinContent"
}
TERM_ID = 'feedConversionRatioNitrogen'


def run(cycle: dict, feed: float):
    inputs = get_feed_inputs(cycle)
    return list_sum(non_empty_list([
        get_node_property_value_converted(MODEL, input, 'crudeProteinContent', default=0, term=TERM_ID) / 6.25
        for input in inputs
    ]))
