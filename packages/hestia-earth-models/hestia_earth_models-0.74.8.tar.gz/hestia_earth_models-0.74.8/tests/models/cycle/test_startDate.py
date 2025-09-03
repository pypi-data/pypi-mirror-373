import pytest

from hestia_earth.models.cycle.startDate import _should_run_by_cycleDuration, _should_run_by_startDate, run


def test_should_run_by_cycleDuration():
    # no endDate => no run
    cycle = {'cycleDuration': 365}
    should_run = _should_run_by_cycleDuration(cycle)
    assert not should_run

    # with startDate missing days => not run
    cycle['endDate'] = '2020-01'
    should_run = _should_run_by_cycleDuration(cycle)
    assert not should_run

    # with endDate full date => run
    cycle['endDate'] = '2020-01-01'
    should_run = _should_run_by_cycleDuration(cycle)
    assert should_run is True


def test_should_run_by_startDate():
    # no startDate => no run
    cycle = {}
    should_run = _should_run_by_startDate(cycle)
    assert not should_run

    # with startDate with days => no run
    cycle['startDate'] = '2020-01-01'
    should_run = _should_run_by_startDate(cycle)
    assert not should_run

    # with startDate no days => run
    cycle['startDate'] = '2020-01'
    should_run = _should_run_by_startDate(cycle)
    assert should_run is True


@pytest.mark.parametrize(
    'test_name,cycle,result',
    [
        (
            'with startDate only', {'startDate': '2020-01'}, '2020-01-15'
        ),
        (
            'with endDate and cycleDuration', {'endDate': '2020-01-01', 'cycleDuration': 365}, '2019-01-01'
        ),
        (
            'with endDate same month as startDate', {'endDate': '2020-02', 'startDate': '2020-02'}, '2020-02-01'
        ),
        (
            'with endDate not same month as startDate', {'endDate': '2020-02', 'startDate': '2020-01'}, '2020-01-15'
        ),
    ]
)
def test_run(test_name: str, cycle: dict, result: str):
    assert run(cycle) == result, test_name
