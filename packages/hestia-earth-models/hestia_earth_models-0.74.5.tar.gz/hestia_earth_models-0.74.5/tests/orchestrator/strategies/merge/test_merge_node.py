from unittest.mock import patch
from hestia_earth.schema import EmissionMethodTier

from hestia_earth.orchestrator.strategies.merge.merge_node import merge, _has_threshold_diff, _should_merge_lower_tier

class_path = 'hestia_earth.orchestrator.strategies.merge.merge_node'


def test_has_threshold_diff():
    key = 'key'
    threshold = 0.1  # 10%
    source = {}
    dest = {}

    # key not in source => merge
    assert _has_threshold_diff(source, dest, key, threshold) is True

    # key not in dest => no merge
    source[key] = [100]
    assert not _has_threshold_diff(source, dest, key, threshold)

    dest[key] = [90]
    assert not _has_threshold_diff(source, dest, key, threshold)

    dest[key] = [89]
    assert _has_threshold_diff(source, dest, key, threshold) is True

    # edge cases
    source[key] = [0]
    dest[key] = [1]
    assert _has_threshold_diff(source, dest, key, threshold) is True

    source[key] = [0]
    dest[key] = [0]
    assert not _has_threshold_diff(source, dest, key, threshold)

    source[key] = [1]
    dest[key] = [0]
    assert _has_threshold_diff(source, dest, key, threshold)


def test_should_merge_lower_tier():
    source = {}
    dest = {}

    # always merge if replacing lower tier
    assert _should_merge_lower_tier(source, dest, {'replaceLowerTier': True}) is True

    # new value has lower tier
    source['methodTier'] = EmissionMethodTier.TIER_3.value
    dest['methodTier'] = EmissionMethodTier.TIER_1.value
    assert not _should_merge_lower_tier(source, dest, {'replaceLowerTier': False})

    source['methodTier'] = EmissionMethodTier.TIER_1.value
    dest['methodTier'] = EmissionMethodTier.NOT_RELEVANT.value
    assert not _should_merge_lower_tier(source, dest, {'replaceLowerTier': False})

    # new value has identical tier
    source['methodTier'] = EmissionMethodTier.TIER_1.value
    dest['methodTier'] = EmissionMethodTier.TIER_1.value
    assert _should_merge_lower_tier(source, dest, {'replaceLowerTier': False}) is True

    # new value has higher tier
    source['methodTier'] = EmissionMethodTier.TIER_1.value
    dest['methodTier'] = EmissionMethodTier.TIER_3.value
    assert _should_merge_lower_tier(source, dest, {'replaceLowerTier': False}) is True


@patch(f"{class_path}._has_threshold_diff", return_value=False)
def test_merge_no_merge(*args):
    source = {'value': [100]}
    dest = {'value': [50]}
    args = {'replaceThreshold': ['value', 50]}
    # simply return the source
    assert merge(source, dest, '0', {}, args) == source


@patch(f"{class_path}._has_threshold_diff", return_value=True)
@patch(f"{class_path}.update_node_version", return_value={})
def test_merge_no_threshold(mock_update, *args):
    source = {'value': [100]}
    dest = {'value': [50]}
    args = {}
    merge(source, dest, '0', {}, args)
    mock_update.assert_called_once()


@patch(f"{class_path}._has_threshold_diff", return_value=True)
@patch(f"{class_path}.update_node_version", return_value={})
def test_merge_with_threshold(mock_update, *args):
    source = {'value': [100]}
    dest = {'value': [50]}
    args = {'replaceThreshold': ['value', 50]}
    merge(source, dest, '0', {}, args)
    mock_update.assert_called_once()
