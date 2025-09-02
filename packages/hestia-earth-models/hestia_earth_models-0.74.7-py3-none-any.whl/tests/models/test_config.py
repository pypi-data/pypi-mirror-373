import importlib

import pytest
from hestia_earth.utils.tools import flatten

from hestia_earth.models.config import (
    load_config,
    config_max_stage,
    _is_aggregated_model,
    _remove_aggregated,
    _use_aware_1,
    load_run_config,
    load_trigger_config,
    get_max_stage,
    AWARE_VERSION
)

_aggregated_model = {
    "value": "input.hestiaAggregatedData"
}
_other_model = {
    "value": "otherModel"
}


def test_load_config():
    node_type = 'Cycle'
    config = load_config(node_type)
    assert config.get('models') is not None


def test_load_config_error():
    node_type = 'Unkown'

    with pytest.raises(Exception, match='Invalid type Unkown.'):
        load_config(node_type)


def test_load_config_skip_aggregated_models():
    node_type = 'Cycle'
    all_models = load_config(node_type, skip_aggregated_models=False).get('models')
    models_no_aggregated = load_config(node_type, skip_aggregated_models=True).get('models')
    assert all_models != models_no_aggregated


def test_load_config_use_aware_v1_site():
    node_type = 'Site'
    v1_models = load_config(node_type, use_aware_version=AWARE_VERSION.V1).get('models')
    v2_models = load_config(node_type, use_aware_version=AWARE_VERSION.V2).get('models')
    assert v1_models != v2_models


def test_load_config_use_aware_v1_impact_assessment():
    node_type = 'ImpactAssessment'
    v1_models = load_config(node_type, use_aware_version=AWARE_VERSION.V1).get('models')
    v2_models = load_config(node_type, use_aware_version=AWARE_VERSION.V2).get('models')
    assert v1_models != v2_models


def test_config_max_stage():
    node_type = 'Cycle'
    config = load_config(node_type)
    assert config_max_stage(config) == 2


def test_is_aggregated_model():
    assert _is_aggregated_model(_aggregated_model) is True
    assert not _is_aggregated_model(_other_model)


def test_remove_aggregated():
    models = [
        [_aggregated_model, _other_model],
        _aggregated_model, _other_model
    ]
    assert _remove_aggregated(models) == [[_other_model], _other_model]


def test_use_aware_1():
    scarcity_model = {
        "model": "aware2-0",
        "value": "scarcityWeightedWaterUse"
    }
    basinid_model = {
        "model": "geospatialDatabase",
        "value": "awareWaterBasinId"
    }
    models = [
        [scarcity_model],
        basinid_model
    ]
    assert _use_aware_1(models) == [
        [{
            "model": "aware",
            "value": "scarcityWeightedWaterUse"
        }],
        {
            "model": "geospatialDatabase",
            "value": "awareWaterBasinId_v1"
        }
    ]


def test_load_run_config():
    assert len(load_run_config(node_type='Site', stage=1)) == 0
    assert len(load_run_config(node_type='Site', stage=2)) == 1


def test_load_run_config_invalid_stage():
    with pytest.raises(Exception) as e:
        load_run_config(
            node_type='ImpactAssessment',
            stage=2
        )
        assert str(e.value) == 'Invalid stage configuration for ImpactAssessment: 2'


def test_load_trigger_config_config():
    assert len(load_trigger_config(node_type='Site', stage=1)) == 1
    assert len(load_trigger_config(node_type='Site', stage=2)) == 1


def test_load_trigger_config_invalid_stage():
    with pytest.raises(Exception) as e:
        load_trigger_config(
            node_type='ImpactAssessment',
            stage=2
        )
        assert str(e.value) == 'Invalid stage configuration for ImpactAssessment: 2'


# included in orchestrator
_ignore_models = ['emissions.deleted', 'transformations']
_ignore_values = [None, '', 'all']


def _model_path(model: dict):
    name = model.get('model').replace('-', '_')
    value = model.get('value')
    suffix = f"hestia_earth.models.{name}"
    return f"{suffix}.{value}" if value not in _ignore_values else suffix


def _get_models_paths(node_type: str):
    models = flatten(load_config(node_type).get('models', []))
    return [
        _model_path(m)
        for m in models
        if m.get('model') not in _ignore_models
    ]


@pytest.mark.parametrize(
    'node_type',
    ['Cycle', 'Site', 'ImpactAssessment']
)
def test_load_config_cycle(node_type: str):
    paths = _get_models_paths(node_type)

    for path in paths:
        run = importlib.import_module(path).run
        assert run is not None, path


@pytest.mark.parametrize(
    'node_type, max_stage',
    [('Cycle', 2), ('Site', 2), ('ImpactAssessment', 1)]
)
def test_get_max_stage(node_type: str, max_stage: int):
    assert get_max_stage(node_type) == max_stage, node_type
