from hestia_earth.models.utils.liveAnimal import get_default_digestibility


def test_get_default_digestibility_valid():
    cycle = {
        'products': [
            {'term': {'@id': 'pig', 'termType': 'liveAnimal'}}
        ],
        'practices': [
            {'term': {'@id': 'freeRangeSystem', 'termType': 'system'}}
        ]
    }
    assert get_default_digestibility('model', 'term_id', cycle) == 60


def test_get_default_digestibility_none():
    # no system => no value
    cycle = {
        'products': [
            {'term': {'@id': 'pig', 'termType': 'liveAnimal'}}
        ]
    }
    assert get_default_digestibility('model', 'term_id', cycle) is None

    # no alue for system
    cycle = {
        'products': [
            {'term': {'@id': 'pig', 'termType': 'liveAnimal'}}
        ],
        'practices': [
            {'term': {'@id': 'permaculture', 'termType': 'system'}}
        ]
    }
    assert get_default_digestibility('model', 'term_id', cycle) is None
