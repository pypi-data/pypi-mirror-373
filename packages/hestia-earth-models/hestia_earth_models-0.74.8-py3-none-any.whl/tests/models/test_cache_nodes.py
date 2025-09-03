import json
from unittest.mock import patch
from tests.utils import fixtures_path

from hestia_earth.models.cache_nodes import _cache_related_nodes, _cache_sources

class_path = 'hestia_earth.models.cache_nodes'
fixtures_folder = f"{fixtures_path}/cache_nodes"


def test_cache_related_nodes():
    with open(f"{fixtures_folder}/nodes.json_no_validate", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/cache_related_nodes/result.json_no_validate", encoding='utf-8') as f:
        expected = json.load(f)

    result = _cache_related_nodes(data.get('nodes'))
    assert result == expected


@patch(f"{class_path}.find_sources", return_value=['source1'])
def test_cache_sources(*args):
    with open(f"{fixtures_folder}/nodes.json_no_validate", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/cache_sources/result.json_no_validate", encoding='utf-8') as f:
        expected = json.load(f)

    result = _cache_sources(data.get('nodes'))
    assert result == expected
