from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.model import linked_node

from .method import include_methodModel
from .term import download_term


def _new_indicator(
    term: dict, model=None,
    land_cover_id: str = None, previous_land_cover_id: str = None, country_id: str = None, key_id: str = None
):
    node = {'@type': SchemaType.INDICATOR.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(term))
    if land_cover_id:
        node['landCover'] = linked_node(download_term(land_cover_id, TermTermType.LANDCOVER))
    if previous_land_cover_id:
        node['previousLandCover'] = linked_node(download_term(previous_land_cover_id, TermTermType.LANDCOVER))
    if country_id:
        node['country'] = linked_node(download_term(country_id, TermTermType.REGION))
    if key_id:
        node['key'] = linked_node(download_term(key_id))
    return include_methodModel(node, model)
