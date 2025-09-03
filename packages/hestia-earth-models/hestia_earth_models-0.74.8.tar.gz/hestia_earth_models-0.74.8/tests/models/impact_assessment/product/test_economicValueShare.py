import json
from tests.utils import fixtures_path

from hestia_earth.models.impact_assessment.product.economicValueShare import MODEL_KEY, _should_run, run

fixtures_folder = f"{fixtures_path}/impact_assessment/product/{MODEL_KEY}"


def test_should_run():
    # no cycle => no run
    impact = {}
    should_run, *args = _should_run(impact)
    assert not should_run

    # with cycle no products => no run
    cycle = {'products': []}
    impact['cycle'] = cycle
    should_run, *args = _should_run(impact)
    assert not should_run

    # with product
    product = {'term': {'@id': 'term'}}
    cycle['products'].append(product)
    should_run, *args = _should_run(impact)
    assert should_run is True


def test_run():
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
