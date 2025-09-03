from unittest.mock import patch
import pydash

from hestia_earth.orchestrator.utils import reset_index
from hestia_earth.orchestrator.strategies.merge.merge_list import merge, _get_value

class_path = 'hestia_earth.orchestrator.strategies.merge.merge_list'
version = '1'


def test_get_value():
    assert _get_value({'startDate': '2020-01-01'}, 'startDate', {}) == '2020-01-01'
    assert _get_value({'startDate': '2020-01-01'}, 'startDate', {'matchDatesFormat': '%Y'}) == '2020'
    assert _get_value({'startDate': '2020-01-01'}, 'startDate', {'matchDatesFormat': '%Y-%m'}) == '2020-01'
    assert _get_value({'startDate': '2020-01-01'}, 'startDate', {'matchDatesFormat': '%Y-%m-%d'}) == '2020-01-01'
    assert _get_value({'value': 500}, 'value') == 500
    assert _get_value({'value': 500}, 'value', {'matchDatesFormat': '%Y-%m-%d'}) == 500
    assert _get_value({'value': 'test'}, 'value') == 'test'


def _default_merge(a, b, *args): return pydash.objects.merge({}, a, b)


@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_new_node(*args):
    old_node = {
        'term': {'@id': 'old-term'},
        'value': 1
    }
    new_node = {
        'term': {'@id': 'new-term'},
        'value': 2
    }
    result = merge([old_node], [new_node], version)
    assert result == [old_node, new_node]


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_existing_node(*args):
    term = {'@id': 'term'}

    node_type = 'Site'
    model = {'key': 'measurements'}

    # with different value => should merge
    old_node = {
        'term': term,
        'value': 1
    }
    new_node = {
        'term': term,
        'value': 2
    }
    result = merge([old_node], [new_node], version, model=model, node_type=node_type)
    assert len(result) == 1

    # with different depths => should not merge
    result = merge([{
        **old_node,
        'depthUpper': 100
    }, {
        **old_node,
        'depthUpper': 150
    }], [{
        **new_node,
        'depthUpper': 50
    }], version, model=model, node_type=node_type)
    assert len(result) == 3
    reset_index()

    node_type = 'Cycle'
    model = {'key': 'emissions'}

    # with same inputs => should merge
    result = merge([{
        **old_node,
        'inputs': [{'@id': 'input-1'}]
    }], [{
        **new_node,
        'inputs': [{'@id': 'input-1'}]
    }], version, model=model, node_type=node_type)
    assert len(result) == 1
    reset_index()

    # with different inputs => should not merge
    result = merge([{
        **old_node,
        'inputs': [{'@id': 'input-1'}]
    }], [{
        **new_node,
        'inputs': [{'@id': 'input-2'}]
    }], version, model=model, node_type=node_type)
    assert len(result) == 2
    reset_index()

    result = merge([{
        **old_node,
        'inputs': [{'@id': 'input-1'}]
    }], [{
        **new_node,
        'inputs': [{'@id': 'input-1'}, {'@id': 'input-2'}]
    }], version, model=model, node_type=node_type)
    assert len(result) == 2
    reset_index()

    # with no inputs => should not merge
    result = merge([old_node], [{
        **new_node,
        'inputs': [{'@id': 'input-2'}]
    }], version, model=model, node_type=node_type)
    assert len(result) == 2


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_existing_node_skip_same_term(*args):
    term = {'@id': 'term'}
    node_type = 'Site'
    model = {'key': 'measurements'}

    old_node = {
        'term': term,
        'value': 1
    }
    new_node = {
        'term': term,
        'value': 2
    }
    result = merge([old_node], [new_node], version, model, {'skipSameTerm': True}, node_type)
    assert len(result) == 1
    assert result[0]['value'] == 1


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_existing_node_new_unique_key(*args):
    term = {'@id': 'term'}
    node_type = 'Cycle'
    model = {'key': 'inputs'}

    old_node = {
        'term': term,
        'value': 1
    }
    new_node = {
        'term': term,
        'value': 1,
        'impactAssessment': {'@id': 'ia-1'}
    }
    result = merge([old_node], [new_node], version, model, {}, node_type)
    assert len(result) == 1
    assert result[0]['impactAssessment'] == {'@id': 'ia-1'}


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_authors(*args):
    node_type = 'Bibliography'
    model = {'key': 'authors'}

    old_node = {
        'lastName': 'name 1'
    }
    new_node = {
        'lastName': 'name 2'
    }
    result = merge([old_node], [new_node], version, model, {}, node_type)
    # no unique keys, should just append data
    assert result == [old_node, new_node]


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_different_terms_same_unique_properties(*args):
    method = {'@id': 'method1'}
    operation = {'@id': 'operation1'}
    inputs = [{'@id': 'input1'}, {'@id': 'input2'}]
    node_type = 'ImpactAssessment'
    model = {'key': 'emissionsResourceUse'}

    node1 = {
        'term': {'@id': 'term1'},
        'value': 1,
        'methodModel': method,
        'operation': operation,
        'inputs': inputs
    }
    node2 = {
        'term': {'@id': 'term2'},
        'value': 2,
        'methodModel': method,
        'operation': operation,
        'inputs': inputs
    }
    node3 = {
        'term': {'@id': 'term3'},
        'value': 3,
        'inputs': inputs
    }
    node4 = {
        'term': {'@id': 'term1'},
        'value': 2,
        'methodModel': method,
        'operation': operation,
        'inputs': inputs
    }
    # different term should not merge
    assert merge([node1], [node2], version, model, {'sameMethodModel': True}, node_type) == [node1, node2]
    assert merge([node1, node2], [node3], version, model, {'sameMethodModel': True}, node_type) == [node1, node2, node3]
    assert merge([node1], [node2, node3], version, model, {}, node_type) == [node1, node2, node3]
    # same term, methodModel, operation and inputs should merge
    assert merge([node1], [node4], version, model, {}, node_type) == [node4]


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_multiple_identical_terms(*args):
    term1 = {'@id': 'term1'}
    node_type = 'Cycle'
    model = {'key': 'inputs'}

    node1 = {
        'term': term1,
        'value': 1
    }
    node2 = {
        'term': term1,
        'value': 2,
        'impactAssessment': {'id': 'ia-1'}
    }
    # merging the same unique nodes should make no changes
    result = merge([node1, node2], [node1, node2], version, model, {}, node_type)
    assert result == [node1, node2]

    # adding the same first node with a new unique key
    node3 = {
        'term': term1,
        'value': 3,
        'impactAssessment': {'@id': 'ia-1'}
    }
    result = merge([node1, node2], [node3], version, model, {}, node_type)
    assert result == [node3, node2]

    node4 = {
        'term': term1,
        'value': 4,
        'impactAssessment': {'id': 'ia-1'}
    }
    result = merge([node1, node2], [node4], version, model, {}, node_type)
    assert result == [node1, node4]


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_animals(*args):
    term1 = {'@id': 'term1'}
    node_type = 'Cycle'
    model = {'key': 'animals'}

    node1 = {
        'animalId': 'animal-1',
        'term': term1,
        'value': 1,
        'properties': [
            {
                'term': {"@id": "liveweightPerHead"},
                'value': 40
            }
        ]
    }
    node2 = {
        'animalId': 'animal-2',
        'term': term1,
        'value': 1,
        'properties': [
            {
                'term': {"@id": "liveweightPerHead"},
                'value': 40
            },
            {
                'term': {"@id": "age"},
                'value': 10
            }
        ]
    }
    result = merge([node1], [node2], version, model, {}, node_type)
    # can not merge as properties is used to determine uniqueness
    assert result == [node1, node2]


@patch(f"{class_path}.merge_node", side_effect=_default_merge)
@patch(f"{class_path}.update_node_version", side_effect=lambda _v, n: n)
def test_merge_with_properties(*args):
    node_type = 'Cycle'
    model = {'key': 'inputs'}

    node1 = {
      "term": {
        "@type": "Term",
        "@id": "concentrateFeedBlend"
      },
      "isAnimalFeed": True,
      "value": [
        100
      ],
      "impactAssessment": {
        "@id": "_djxbkdk2wnx",
        "@type": "ImpactAssessment"
      },
      "impactAssessmentIsProxy": False,
      "@type": "Input"
    }

    node2 = {
      "term": {
        "@type": "Term",
        "@id": "concentrateFeedBlend"
      },
      "isAnimalFeed": True,
      "value": [
        200
      ],
      "impactAssessment": {
        "@id": "uug7pcaas6aa",
        "@type": "ImpactAssessment"
      },
      "impactAssessmentIsProxy": False,
      "@type": "Input"
    }

    properties = [
        {
            'term': {'@id': 'property-1'},
            'value': 100
        }
    ]
    node3 = node2 | {'properties': properties}

    result = merge([node1, node2], [node3], version, model, {}, node_type)
    # can not merge as properties is used to determine uniqueness
    assert result == [node1, node3]
