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
LOOKUPS = {
    "crop-property": "energyContentHigherHeatingValue"
}
TERM_ID = 'feedConversionRatioEnergy'


def run(cycle: dict, feed: float): return feed
