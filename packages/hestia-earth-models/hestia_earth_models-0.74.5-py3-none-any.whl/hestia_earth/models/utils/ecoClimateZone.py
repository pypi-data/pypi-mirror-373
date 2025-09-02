from enum import Enum
from functools import reduce
from typing import Any, Optional, Union

from hestia_earth.schema import NodeType

from hestia_earth.utils.blank_node import get_node_value
from hestia_earth.utils.lookup import download_lookup, _get_single_table_value, column_name, extract_grouped_data
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import safe_parse_float


class EcoClimateZone(Enum):
    """
    Enum representing eco-climate zones. The value of each member of the Enum correctly corresponds with the values of
    `ecoClimateZone` term and the `ecoClimateZone-lookup.csv`.
    """
    WARM_TEMPERATE_MOIST = 1
    WARM_TEMPERATE_DRY = 2
    COOL_TEMPERATE_MOIST = 3
    COOL_TEMPERATE_DRY = 4
    POLAR_MOIST = 5
    POLAR_DRY = 6
    BOREAL_MOIST = 7
    BOREAL_DRY = 8
    TROPICAL_MONTANE = 9
    TROPICAL_WET = 10
    TROPICAL_MOIST = 11
    TROPICAL_DRY = 12


def get_eco_climate_zone_value(node: dict, as_enum: bool = False) -> Union[int, EcoClimateZone, None]:
    """
    Get the eco-climate zone value from a Site.

    Parameters
    ----------
    node : dict
        A HESTIA [Site](https://hestia.earth/schema/Site) or
        [Cycle](https://hestia.earth/schema/Cycle).

    Returns
    -------
    int | None
        The eco-climate zone value if found, otherwise `None`.
    """
    site = (
        node.get("site", {}) if node.get("@type") == NodeType.CYCLE.value
        else node if node.get("@type") == NodeType.SITE.value
        else {}
    )
    eco_climate_zone = find_term_match(site.get("measurements", []), "ecoClimateZone")
    value = get_node_value(eco_climate_zone, default=None)
    return _eco_climate_zone_node_value_to_enum(value) if as_enum else value


def _eco_climate_zone_node_value_to_enum(value: Optional[int]) -> Optional[EcoClimateZone]:
    """
    Safe conversion between int (`ecoClimateZone` measurement node value) and `EcoClimateZone` enum members.

    If node value is invalid, return `None`.
    """
    should_run = isinstance(value, int) and 1 <= value <= 12
    return EcoClimateZone(value) if should_run else None


def get_ecoClimateZone_lookup_value(eco_climate_zone: str, col_name: str, group_name: str = None) -> float:
    """
    Get a value from the `ecoClimateZone` lookup table.

    Parameters
    ----------
    eco_climate_zone : str
        The `ecoClimateZone` as a string.
    col_name : str
        The name of the column in the lookup table.
    group_name : str
        Optional - the name of the group if the data is in the format `group1:value1;group2:value2`.

    Returns
    -------
    float
        The value associated with the `ecoClimateZone`.
    """
    try:
        lookup = download_lookup('ecoClimateZone.csv')
        code = int(str(eco_climate_zone))
        data = _get_single_table_value(lookup, column_name('ecoClimateZone'), code, column_name(col_name))
        return safe_parse_float(
            data if group_name is None else extract_grouped_data(data, group_name), default=None
        )
    except Exception:
        return 0


def get_ecoClimateZone_lookup_grouped_value(
    eco_climate_zone: str, col_name: str, default: Any = None
) -> Optional[dict]:
    """
    Get a grouped value from the `ecoClimateZone` lookup table formatted as a dictionary

    Parameters
    ----------
    eco_climate_zone : str
        The `ecoClimateZone` as a string.
    col_name : str
        The name of the column in the lookup table.
    default : Any, optional
        The default value to return if no lookup value, or invalid lookup value is retrieved.

    Returns
    -------
    float
        The value associated with the `ecoClimateZone`.
    """
    try:
        lookup = download_lookup('ecoClimateZone.csv')
        code = int(str(eco_climate_zone))
        data = _get_single_table_value(lookup, column_name('ecoClimateZone'), code, column_name(col_name))
        grouped_data = reduce(
            lambda prev, curr: prev | {curr.split(':')[0]: safe_parse_float(curr.split(':')[1], default=None)},
            data.split(';'),
            {}
        ) if data is not None and isinstance(data, str) and len(data) > 1 else default
        return grouped_data
    except Exception:
        return default
