from hestia_earth.models.ipcc2019.n2OToAir_indirect_emissions_utils import _should_run
from hestia_earth.models.ipcc2019.n2OToAirCropResidueDecompositionIndirect import _EMISSION_IDS


def test_should_run():
    # no emissions => no run
    cycle = {'completeness': {'cropResidue': True}, 'emissions': []}
    should_run, *args = _should_run('', _EMISSION_IDS, cycle)
    assert not should_run

    # with no3 emission => run
    cycle['emissions'] = [
        {
            'term': {'@id': id},
            'value': [100]
        } for id in _EMISSION_IDS
    ]
    should_run, *args = _should_run('', _EMISSION_IDS, cycle)
    assert should_run is True
