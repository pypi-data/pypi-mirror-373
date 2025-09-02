from unittest.mock import patch

from hestia_earth.models.utils.cache_sources import CACHE_KEY, CACHE_SOURCES_KEY, _has_value, cache_sources

class_path = 'hestia_earth.models.utils.cache_sources'
sources = {'source a': {'@type': 'Source', '@id': 'source-1'}}


def test_should_run():
    # no existing cache => run
    assert not _has_value({CACHE_KEY: {}})
    assert not _has_value({CACHE_KEY: {CACHE_SOURCES_KEY: {}}})

    # with existing cache => no run
    assert _has_value({CACHE_KEY: {CACHE_SOURCES_KEY: {'sample': 'a'}}}) is True


@patch(f"{class_path}.find_sources", return_value=sources)
def test_run(*args):
    result = cache_sources({})
    assert result.get(CACHE_KEY).get(CACHE_SOURCES_KEY) == sources
