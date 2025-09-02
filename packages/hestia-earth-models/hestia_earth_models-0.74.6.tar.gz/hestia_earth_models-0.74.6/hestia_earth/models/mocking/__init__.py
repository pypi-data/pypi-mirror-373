import os

from hestia_earth.models.utils import measurement, site
from .mock_search import mock as mock_search

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(CURRENT_DIR, 'search-results.json')


def enable_mock(filepath: str, node: dict = None, keep_in_memory: bool = False):
    # apply mocks on search results
    mock_search(filepath, keep_in_memory)

    if node is not None:
        # skip fetch bibliography data
        measurement.include_source = lambda v, *args: v

        # mock related cycles to return the current node
        fake_node = {'@id': 'fake-cycle', **node}
        site.download_hestia = lambda *args: fake_node
        site.find_related = lambda *args: [fake_node]
