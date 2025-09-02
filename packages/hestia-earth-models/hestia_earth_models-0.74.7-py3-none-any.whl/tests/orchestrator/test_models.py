from unittest.mock import patch
import pytest
import json
import os

from tests.utils import fixtures_path
from hestia_earth.orchestrator.models import run, _run_parallel, _filter_models_stage

class_path = 'hestia_earth.orchestrator.models'
folder_path = os.path.join(fixtures_path, 'orchestrator', 'cycle')


@patch('hestia_earth.models.utils.source.find_sources', return_value=[])
@patch('hestia_earth.orchestrator.strategies.merge._merge_version', return_value='0.0.0')
def test_run(*args):
    with open(os.path.join(folder_path, 'config.json'), encoding='utf-8') as f:
        config = json.load(f)
    with open(os.path.join(folder_path, 'cycle.jsonld'), encoding='utf-8') as f:
        cycle = json.load(f)
    with open(os.path.join(folder_path, 'result.jsonld'), encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle, config.get('models'))
    assert result == expected


@patch(f"{class_path}._run_model", side_effect=Exception('error'))
def test_run_parallel_with_errors(*args):
    data = {
        '@type': 'Cycle',
        '@id': 'cycle'
    }
    model = [{'key': 'model1'}, {'key': 'model2'}]

    with pytest.raises(Exception):
        _run_parallel(data, model, [])


def test_filter_models_stage():
    models = json.load(open(os.path.join(fixtures_path, 'orchestrator', 'stages', 'config.json'))).get('models')
    assert _filter_models_stage(models) == models
    assert _filter_models_stage(models, 1) == [
        {
            "key": "model1",
            "stage": 1
        },
        {
            "key": "model2",
            "stage": 1
        }
    ]
    assert _filter_models_stage(models, 2) == [
        [
            {
                "key": "model3",
                "stage": 2
            },
            {
                "key": "model4",
                "stage": 2
            }
        ]
    ]
    assert _filter_models_stage(models, 3) == [
        {
            "key": "model5",
            "stage": 3
        }
    ]
    assert _filter_models_stage(models, [1, 2, 3]) == models
