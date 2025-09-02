from tests.utils import SITE

from hestia_earth.models.cycle.post_checks.otherSites import run


def test_run_no_otherSites():
    cycle = {}
    value = run(cycle)
    assert 'otherSites' not in value


def test_run():
    cycle = {'otherSites': [SITE]}
    value = run(cycle)
    assert value['otherSites'] == [{'@type': SITE['@type'], '@id': SITE['@id']}]
