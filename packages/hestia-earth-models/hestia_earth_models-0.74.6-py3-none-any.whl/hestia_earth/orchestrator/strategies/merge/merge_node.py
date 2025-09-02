import pydash
from hestia_earth.schema import EmissionMethodTier

from hestia_earth.orchestrator.log import logger, logShouldMerge
from hestia_earth.orchestrator.utils import update_node_version, _average

_METHOD_TIER_ORDER = [
    EmissionMethodTier.NOT_RELEVANT.value,
    EmissionMethodTier.TIER_1.value,
    EmissionMethodTier.TIER_2.value,
    EmissionMethodTier.TIER_3.value,
    EmissionMethodTier.MEASURED.value,
    EmissionMethodTier.BACKGROUND.value
]


def _has_threshold_diff(source: dict, dest: dict, key: str, threshold: float):
    term_id = dest.get('term', {}).get('@id', dest.get('@id'))
    source_value = _average(source.get(key), None)
    dest_value = _average(dest.get(key), None)
    delta = None if any([source_value is None, dest_value is None]) else (
        abs(source_value - dest_value) / (1 if source_value == 0 else source_value)
    )
    should_merge = source_value is None or (delta is not None and delta > threshold)
    logger.debug('merge %s for %s with threshold=%s, delta=%s: %s', key, term_id, threshold, delta, should_merge)
    return should_merge


def _should_merge_threshold(source: dict, dest: dict, args: dict):
    [key, threshold] = args.get('replaceThreshold', [None, 0])
    return True if key is None else _has_threshold_diff(source, dest, key, threshold)


def _should_merge_lower_tier(source: dict, dest: dict, args: dict):
    source_tier = _METHOD_TIER_ORDER.index(source.get('methodTier', _METHOD_TIER_ORDER[0]))
    dest_tier = _METHOD_TIER_ORDER.index(dest.get('methodTier', _METHOD_TIER_ORDER[-1]))
    term_id = dest.get('term', {}).get('@id', dest.get('@id'))
    should_merge = args.get('replaceLowerTier', False) or dest_tier >= source_tier
    logger.debug('merge for %s with original tier=%s, new tier=%s: %s',
                 term_id, source.get('methodTier'), dest.get('methodTier'), should_merge)
    return should_merge


_MERGE_FROM_ARGS = {
    'replaceThreshold': _should_merge_threshold,
    'replaceLowerTier': _should_merge_lower_tier
}


def merge(source: dict, dest: dict, version: str, model: dict = {}, merge_args: dict = {}, *args):
    merge_args = {
        key: func(source, dest, merge_args) for key, func in _MERGE_FROM_ARGS.items()
    } if source is not None else {}
    term_id = dest.get('term', {}).get('@id', dest.get('@id'))

    should_merge = all([v for _k, v in merge_args.items()])
    logShouldMerge(source, model.get('model'), term_id, should_merge, key=model.get('key'), value=term_id, **merge_args)

    return update_node_version(version, pydash.objects.merge({}, source, dest), source) if should_merge else source
