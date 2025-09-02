from unittest.mock import patch
import pytest

from hestia_earth.orchestrator import run

config = {'models': []}


@patch('hestia_earth.orchestrator.run_models', return_value={})
def test_run(mock_run_models, *args):
    run({'@type': 'Cycle'}, config)
    mock_run_models.assert_called_once()


def test_run_missing_type():
    with pytest.raises(Exception, match='Please provide an "@type" key in your data.'):
        run({}, config)


def test_run_missing_config():
    with pytest.raises(Exception, match='Please provide a valid configuration.'):
        run({'@type': 'Cycle'}, None)


def test_run_missing_models():
    with pytest.raises(Exception, match='Please provide a valid configuration.'):
        run({'@type': 'Cycle'}, {})
