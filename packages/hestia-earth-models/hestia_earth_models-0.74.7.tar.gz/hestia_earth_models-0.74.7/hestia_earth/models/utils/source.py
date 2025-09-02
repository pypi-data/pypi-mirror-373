import pathlib
from os.path import dirname, abspath, join
import re
from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import find_node_exact, search
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import flatten, non_empty_list

from . import cached_value

ROOT_DIR = abspath(join(dirname(abspath(__file__)), '..'))
CACHE_SOURCES_KEY = 'sources'


def _find_source(biblio_title: str = None):
    source = find_node_exact(SchemaType.SOURCE, {'bibliography.title': biblio_title}) if biblio_title else None
    return None if source is None else linked_node({'@type': SchemaType.SOURCE.value, **source})


def get_source(node: dict, biblio_title: str = None, other_biblio_titles: list = []):
    source = cached_value(node, CACHE_SOURCES_KEY, {}).get(biblio_title) or _find_source(biblio_title)
    other_sources = non_empty_list([
        (cached_value(node, CACHE_SOURCES_KEY, {}).get(title) or _find_source(title))
        for title in other_biblio_titles
    ])
    return (
        {'source': source} if source else {}
    ) | (
        {'otherSources': other_sources} if other_sources else {}
    )


def _extract(content: str):
    return [
        str(m).replace("BIBLIO_TITLE = ", '').replace("'", '')
        for m in re.findall(r'BIBLIO_TITLE = \'[^\']*\'', content)
    ] + flatten([
        str(m).replace(
            "OTHER_BIBLIO_TITLES = [", ''
        ).replace(
            '  ', ''
        ).replace(
            "'", ''
        ).replace(
            "]", ''
        ).replace(
            '# noqa: E501', ''
        ).split(',')
        for m in re.findall(r'OTHER_BIBLIO_TITLES = \[[^[]*\]', content)
    ])


def _list_sources():
    dir = pathlib.Path(ROOT_DIR)
    # ignore current file
    files = list(filter(lambda f: not str(f).endswith('utils/source.py'), list(dir.rglob('**/*.py'))))
    return list(set(flatten([_extract(open(f, 'r').read().replace('\n', '')) for f in files])))


def find_sources():
    titles = _list_sources()
    query = {
        'bool': {
            'must': [{'match': {'@type': SchemaType.SOURCE.value}}],
            'should': [{'match': {'bibliography.title.keyword': title}} for title in titles],
            'minimum_should_match': 1
        }
    }
    results = search(query, fields=['@type', '@id', 'name', 'bibliography.title'], limit=len(titles))
    return {result.get('bibliography').get('title'): linked_node(result) for result in results}
