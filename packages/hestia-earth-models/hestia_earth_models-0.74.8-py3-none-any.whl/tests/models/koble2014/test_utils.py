from unittest.mock import patch
from tests.utils import RESIDUE_TERMS

from hestia_earth.models.koble2014 import MODEL
from hestia_earth.models.koble2014.utils import _should_run

class_path = '.'.join(['hestia_earth', 'models', MODEL, 'utils'])


@patch(f"hestia_earth.models.{MODEL}.utils.get_crop_residue_management_terms", return_value=RESIDUE_TERMS)
@patch(f"{class_path}.find_primary_product", return_value={})
def test_should_run(*args):
    cycle = {'completeness': {'cropResidue': False}}

    # with 100% practices => no run
    cycle['practices'] = [
        {
            'term': {'termType': 'cropResidueManagement', '@id': RESIDUE_TERMS[0]},
            'value': [100]
        }
    ]
    should_run, *ars = _should_run('', cycle)
    assert not should_run

    # with below 100% practices => run
    cycle['practices'] = [
        {
            'term': {'termType': 'cropResidueManagement', '@id': RESIDUE_TERMS[0]},
            'value': [50]
        }
    ]
    should_run, *ars = _should_run('', cycle)
    assert should_run is True

    # requires country / no country => no run
    should_run, *ars = _should_run('', cycle, require_country=True)
    assert not should_run

    # requires country / with country => run
    cycle['site'] = {'country': {'@id': 'GADM-GBR'}}
    should_run, *ars = _should_run('', cycle, require_country=True)
    assert should_run is True

    # with existing product => no run
    cycle['products'] = [
        {
            'term': {'termType': 'cropResidue', '@id': 'aboveGroundCropResidueRemoved'},
            'value': [50]
        }
    ]
    should_run, *ars = _should_run('', cycle)
    assert not should_run
