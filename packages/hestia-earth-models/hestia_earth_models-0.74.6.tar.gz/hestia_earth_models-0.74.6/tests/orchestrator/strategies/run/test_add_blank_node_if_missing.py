from unittest.mock import patch

from hestia_earth.orchestrator.strategies.run.add_blank_node_if_missing import should_run

class_path = 'hestia_earth.orchestrator.strategies.run.add_blank_node_if_missing'
FAKE_EMISSION = {'@id': 'n2OToAirCropResidueDecompositionIndirect', 'termType': 'emission'}


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run(mock_node_exists, *args):
    data = {}
    model = {}

    # node does not exists => run
    mock_node_exists.return_value = None
    assert should_run(data, model) is True

    # node exists but no value => run
    mock_node_exists.return_value = {}
    assert should_run(data, model) is True

    # node exists with value + no params => no run
    node = {'value': 10}
    mock_node_exists.return_value = node
    assert not should_run(data, model)

    # node exists with added value `0` and `Emission` => run
    node = {'@type': 'Emission', 'value': [0], 'added': ['value'], 'methodTier': 'not relevant'}
    mock_node_exists.return_value = node
    assert should_run(data, model) is True


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run_skipEmptyValue(mock_node_exists, *args):
    data = {}

    # no value and not skip => run
    mock_node_exists.return_value = {}
    model = {'runArgs': {'skipEmptyValue': False}}
    assert should_run(data, model) is True

    # no value and skip => no run
    mock_node_exists.return_value = {}
    model = {'runArgs': {'skipEmptyValue': True}}
    assert not should_run(data, model)


@patch(f"{class_path}.get_required_model_param", return_value='')
def test_should_run_skipAggregated(*args):
    data = {}
    model = {'runArgs': {'skipAggregated': True}}

    # not aggregated => run
    data = {'aggregated': False}
    assert should_run(data, model) is True

    # aggregated => no run
    data = {'aggregated': True}
    assert not should_run(data, model)


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run_runNonAddedTerm(mock_node_exists, *args):
    data = {}
    node = {'value': 10}
    mock_node_exists.return_value = node
    model = {'runArgs': {'runNonAddedTerm': True}}

    # term has been added => no run
    node['added'] = ['term']
    assert not should_run(data, model)

    # term has not been added => run
    node['added'] = []
    assert should_run(data, model) is True


@patch(f"{class_path}.get_required_model_param", return_value='')
@patch(f"{class_path}.find_term_match")
def test_should_run_runNonMeasured(mock_node_exists, *args):
    data = {}
    node = {'value': 10}
    mock_node_exists.return_value = node
    model = {'runArgs': {'runNonMeasured': True}}

    # term measured => no run
    node['methodTier'] = 'measured'
    assert not should_run(data, model)

    # term not measured => run
    node['methodTier'] = 'background'
    assert should_run(data, model) is True


@patch(f"{class_path}.get_required_model_param", return_value=FAKE_EMISSION.get('@id'))
@patch(f"{class_path}.find_term_match")
def test_should_run_check_typeAllowed(mock_node_exists, *args):
    node = {'term': FAKE_EMISSION}
    mock_node_exists.return_value = node
    model = {}

    # type is not allowed => no run
    assert not should_run({'type': 'Transformation'}, model)

    # type is allowed => run
    assert should_run({'type': 'Cycle'}, model) is True
