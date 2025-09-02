from unittest.mock import patch
from tests.utils import SITE

from hestia_earth.models.cycle.pre_checks.otherSites import run

class_path = 'hestia_earth.models.cycle.pre_checks.otherSites'


def test_run_no_otherSites():
    cycle = {}

    value = run(cycle)
    assert 'otherSites' not in value


@patch(f"{class_path}._load_calculated_node", return_value=SITE)
def test_run(*args):
    cycle = {'otherSites': [{'@id': SITE['@id']}]}

    value = run(cycle)
    assert value['otherSites'] == [SITE]
