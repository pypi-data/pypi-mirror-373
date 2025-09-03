from unittest.mock import patch

from hestia_earth.orchestrator.strategies.merge.merge_append import merge

class_path = 'hestia_earth.orchestrator.strategies.merge.merge_append'


@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_new_node(*args):
    node1 = {
        'term': {'@id': 'term-1'},
        'value': 1
    }
    node2 = {
        'term': {'@id': 'term-2'},
        'value': 2
    }
    source = [node1]
    result = merge(source, [node1, node2], '1')
    result = merge(result, node2, '1')
    assert result == [node1, node1, node2, node2]


def test_merge_list():
    source = [1]
    dest = [2, 3]
    assert merge(source, dest, '1') == [1, 2, 3]


def test_merge_el():
    source = [1]
    dest = 2
    assert merge(source, dest, '1') == [1, 2]
