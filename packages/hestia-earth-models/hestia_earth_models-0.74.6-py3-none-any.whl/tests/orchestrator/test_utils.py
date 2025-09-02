from hestia_earth.orchestrator.utils import update_node_version

version = '2'


def test_update_node_version():
    current_data = {
        'key1': 50,
        'key2': 100
    }
    new_data = {
        'key2': 200,
        'key3': 300,
        'key4': {}
    }
    assert update_node_version(version, new_data, current_data) == {
        **new_data,
        'added': ['key3', 'key4'],
        'addedVersion': [version, version],
        'updated': ['key2'],
        'updatedVersion': [version]
    }


def test_update_node_version_deep():
    current_data = {
        'object': {
            'first': True
        },
        'values': [
            {
                'term': {'@type': 'Term'},
                'value': [500],
                'properties': [
                    {
                        'term': {'@type': 'Term', '@id': 'Prop1'},
                        'value': 100
                    }
                ]
            }
        ]
    }
    new_data = {
        'object': {
            'first': True,
            'second': False
        },
        'values': [
            {
                'term': {'@type': 'Term'},
                'value': [500],
                'min': [100],
                'properties': [
                    {
                        'term': {'@type': 'Term', '@id': 'Prop1'},
                        'value': 10
                    },
                    {
                        'term': {'@type': 'Term', '@id': 'Prop2'},
                        'value': 20
                    }
                ]
            },
            {
                'term': {'@type': 'Term', '@id': 'Test2'}
            }
        ]
    }
    result = update_node_version(version, new_data, current_data)
    assert result == {
        'object': {
            'first': True,
            'second': False,
            'added': ['second'],
            'addedVersion': [version]
        },
        'values': [
            {
                'term': {'@type': 'Term'},
                'value': [500],
                'min': [100],
                'properties': [
                    {
                        'term': {'@type': 'Term', '@id': 'Prop1'},
                        'value': 10,
                        'updated': ['value'],
                        'updatedVersion': [version]
                    },
                    {
                        'term': {'@type': 'Term', '@id': 'Prop2'},
                        'value': 20,
                        'added': ['term', 'value'],
                        'addedVersion': [version, version]
                    }
                ],
                'added': ['min'],
                'addedVersion': [version],
                'updated': ['properties'],
                'updatedVersion': [version]
            },
            {
                'term': {'@type': 'Term', '@id': 'Test2'},
                'added': ['term'],
                'addedVersion': [version]
            }
        ],
        'updated': ['object', 'values'],
        'updatedVersion': [version, version]
    }
