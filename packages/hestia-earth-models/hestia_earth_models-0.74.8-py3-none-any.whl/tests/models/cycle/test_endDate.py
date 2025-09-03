import pytest

from hestia_earth.models.cycle.endDate import _should_run, run


def test_should_run():
    # no endDate => no run
    cycle = {}
    should_run = _should_run(cycle)
    assert not should_run

    # with endDate with days => no run
    cycle['endDate'] = '2020-01-01'
    should_run = _should_run(cycle)
    assert not should_run

    # with endDate no days => run
    cycle['endDate'] = '2020-01'
    should_run = _should_run(cycle)
    assert should_run is True


@pytest.mark.parametrize(
    'test_name,cycle,result',
    [
        (
            'with endDate only', {'endDate': '2020-01'}, '2020-01-14'
        ),
        (
            'with endDate same month as startDate', {'endDate': '2020-02', 'startDate': '2020-02'}, '2020-02-29'
        ),
        (
            'with endDate not same month as startDate', {'endDate': '2020-02', 'startDate': '2020-01'}, '2020-02-14'
        ),
    ]
)
def test_run(test_name: str, cycle: dict, result: str):
    assert run(cycle) == result, test_name
