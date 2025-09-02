from ..utils import average_blank_node_properties_value

REQUIREMENTS = {
    "Cycle": {
        "animals": [{
            "@type": "Animal",
            "min": "",
            "max": ""
        }]
    }
}
RETURNS = {
    "Animal": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
MODEL_KEY = 'properties'


def run(cycle: dict):
    return average_blank_node_properties_value(cycle, cycle.get('animals', []))
