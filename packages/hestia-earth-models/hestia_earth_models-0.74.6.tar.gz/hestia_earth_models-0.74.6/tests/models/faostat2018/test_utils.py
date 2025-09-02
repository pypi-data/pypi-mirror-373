from hestia_earth.models.faostat2018.utils import should_run_landTransformationFromCropland


def test_should_run_landTransformationFromCropland():
    impact = {}
    term_id = 'term'

    # no indicator => no run
    should_run, *args = should_run_landTransformationFromCropland(term_id, impact)
    assert not should_run

    # with indicator value 0 => no run
    impact['emissionsResourceUse'] = [{
        'term': {'@id': term_id},
        'previousLandCover': {'@id': 'cropland'},
        'value': 0
    }]
    should_run, *args = should_run_landTransformationFromCropland(term_id, impact)
    assert not should_run

    # with indicator => run
    impact['emissionsResourceUse'] = [{
        'term': {'@id': term_id},
        'previousLandCover': {'@id': 'cropland'},
        'value': 10
    }]
    should_run, *args = should_run_landTransformationFromCropland(term_id, impact)
    assert should_run is True
