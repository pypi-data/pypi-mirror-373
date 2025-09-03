from enum import Enum
from functools import reduce
from math import isclose
from numpy import inf, random
from numpy.typing import NDArray
from typing import Callable, Optional, Union

from hestia_earth.schema import TermTermType
from hestia_earth.utils.blank_node import get_node_value
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.utils.stats import repeat_single, truncated_normal_1d
from hestia_earth.models.utils.blank_node import node_term_match, validate_start_date_end_date
from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone, get_ecoClimateZone_lookup_grouped_value
from hestia_earth.models.utils.term import get_cover_crop_property_terms, get_lookup_value


LOOKUPS = {
    "landCover": "BIOMASS_CATEGORY",
    "ecoClimateZone": [
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_ANNUAL_CROPS",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_COCONUT",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_FOREST",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_GRASSLAND",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_JATROPHA",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_JOJOBA",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_NATURAL_FOREST",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OIL_PALM",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OLIVE",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_ORCHARD",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_PLANTATION_FOREST",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_RUBBER",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_SHORT_ROTATION_COPPICE",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_TEA",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_VINE",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_WOODY_PERENNIAL",
        "AG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER",
        "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_NATURAL_FOREST",
        "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_PLANTATION_FOREST",
        "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"
    ]
}


class BiomassCategory(Enum):
    """
    Enum representing biomass categories, sourced from IPCC (2006), IPCC (2019) and European Commission (2010).

    Enum values formatted for logging as table.
    """
    ANNUAL_CROPS = "annual-crops"
    COCONUT = "coconut"                                             # European Commission (2010)
    FOREST = "forest"                                               # IPCC (2019) recalculated per eco-climate zone
    GRASSLAND = "grassland"
    JATROPHA = "jatropha"                                           # European Commission (2010)
    JOJOBA = "jojoba"                                               # European Commission (2010)
    NATURAL_FOREST = "natural-forest"                               # IPCC (2019) recalculated per eco-climate zone
    OIL_PALM = "oil palm"                                           # IPCC (2019)
    OLIVE = "olive"                                                 # IPCC (2019)
    ORCHARD = "orchard"                                             # IPCC (2019)
    OTHER = "other"
    PLANTATION_FOREST = "plantation-forest"                         # IPCC (2019) recalculated per eco-climate zone
    RUBBER = "rubber"                                               # IPCC (2019)
    SHORT_ROTATION_COPPICE = "short-rotation-coppice"               # IPCC (2019)
    TEA = "tea"                                                     # IPCC (2019)
    VINE = "vine"                                                   # IPCC (2019)
    WOODY_PERENNIAL = "woody-perennial"                             # IPCC (2006)


_BIOMASS_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE = {
    BiomassCategory.ANNUAL_CROPS: "Annual crops",
    BiomassCategory.COCONUT: "Coconut",
    BiomassCategory.FOREST: "Forest",
    BiomassCategory.GRASSLAND: "Grassland",
    BiomassCategory.JATROPHA: "Jatropha",
    BiomassCategory.JOJOBA: "Jojoba",
    BiomassCategory.NATURAL_FOREST: "Natural forest",
    BiomassCategory.OIL_PALM: "Oil palm",
    BiomassCategory.OLIVE: "Olive",
    BiomassCategory.ORCHARD: "Orchard",
    BiomassCategory.OTHER: "Other",
    BiomassCategory.PLANTATION_FOREST: "Plantation forest",
    BiomassCategory.RUBBER: "Rubber",
    BiomassCategory.SHORT_ROTATION_COPPICE: "Short rotation coppice",
    BiomassCategory.TEA: "Tea",
    BiomassCategory.VINE: "Vine",
    BiomassCategory.WOODY_PERENNIAL: "Woody perennial"
}

_TARGET_LAND_COVER = 100

_GROUP_LAND_COVER_BY_BIOMASS_CATEGORY = [
    BiomassCategory.ANNUAL_CROPS,
    BiomassCategory.GRASSLAND,
    BiomassCategory.OTHER,
    BiomassCategory.SHORT_ROTATION_COPPICE
]
"""
Terms associated with these biomass categories can be grouped together when summarising land cover coverage in
`_group_by_term_id`.
"""


def group_by_biomass_category(result: dict[BiomassCategory, float], node: dict) -> dict[BiomassCategory, float]:
    """
    Reducer function for `_group_land_cover_nodes_by` that groups and sums node value by their associated
    `BiomassCategory`.

    Parameters
    ----------
    result : dict
        A dict with the shape `{category (BiomassCategory): sum_value (float), ...categories}`.
    node : dict
        A HESTIA `Management` node with `term.termType` = `landCover`.

    Returns
    -------
    result : dict
        A dict with the shape `{category (BiomassCategory): sum_value (float), ...categories}`.
    """
    biomass_category = _retrieve_biomass_category(node)
    value = get_node_value(node)

    update_dict = {biomass_category: result.get(biomass_category, 0) + value}

    should_run = biomass_category and value
    return result | update_dict if should_run else result


def group_by_term_id(
    result: dict[Union[str, BiomassCategory], float], node: dict
) -> dict[Union[str, BiomassCategory], float]:
    """
    Reducer function for `_group_land_cover_nodes_by` that groups and sums node value by their `term.@id` if a the land
    cover is a woody plant, else by their associated `BiomassCategory`

    Land cover events can be triggered by changes in land cover within the same `BiomassCategory` (e.g., `peachTree` to
    `appleTree`) due to the requirement to clear the previous woody biomass to establish the new land cover.

    Some land covers (e.g., land covers associated with the `BiomassCategory` = `Annual crops`, `Grassland`, `Other` or
    `Short rotation coppice`) are exempt from this rule due to the Tier 1 assumptions that biomass does not accumulate
    within the category or the maturity cycle of the land cover is significantly shorter than the amortisation period of
    20 years.

    Parameters
    ----------
    result : dict
        A dict with the shape `{category (str | BiomassCategory): sum_value (float), ...categories}`.
    node : dict
        A HESTIA `Management` node with `term.termType` = `landCover`.

    Returns
    -------
    result : dict
        A dict with the shape `{category (str | BiomassCategory): sum_value (float), ...categories}`.
    """
    term_id = node.get("term", {}).get("@id")
    biomass_category = _retrieve_biomass_category(node)
    value = get_node_value(node)

    key = biomass_category if biomass_category in _GROUP_LAND_COVER_BY_BIOMASS_CATEGORY else term_id

    update_dict = {key: result.get(key, 0) + value}

    should_run = biomass_category and value
    return result | update_dict if should_run else result


def _retrieve_biomass_category(node: dict) -> Optional[BiomassCategory]:
    """
    Retrieve the `BiomassCategory` associated with a land cover using the `BIOMASS_CATEGORY` lookup.

    If lookup value is missing, return `None`.

    Parameters
    ----------
    node : dict
        A valid `Management` node with `term.termType` = `landCover`.

    Returns
    -------
    BiomassCategory | None
        The associated `BiomassCategory` or `None`
    """
    LOOKUP = LOOKUPS["landCover"]
    term = node.get("term", {})
    lookup_value = get_lookup_value(term, LOOKUP, skip_debug=True)

    return _assign_biomass_category(lookup_value) if lookup_value else None


def summarise_land_cover_nodes(
    land_cover_nodes: list[dict],
    group_by_func: Callable[[dict, dict], dict] = group_by_biomass_category
) -> dict[Union[str, BiomassCategory], float]:
    """
    Group land cover nodes using `group_by_func`.

    Parameters
    ----------
    land_cover_nodes : list[dict]
        A list of HESTIA `Management` nodes with `term.termType` = `landCover`.

    Returns
    -------
    result : dict
        A dict with the shape `{category (str | BiomassCategory): sum_value (float), ...categories}`.
    """
    category_cover = reduce(group_by_func, land_cover_nodes, dict())
    return _rescale_category_cover(category_cover)


def _rescale_category_cover(
    category_cover: dict[Union[BiomassCategory, str], float]
) -> dict[Union[BiomassCategory, str], float]:
    """
    Enforce a land cover coverage of 100%.

    If input coverage is less than 100%, fill the remainder with `BiomassCategory.OTHER`. If the input coverage is
    greater than 100%, proportionally downscale all categories.

    Parameters
    ----------
    category_cover : dict[BiomassCategory | str, float]
        The input category cover dict.

    Returns
    -------
    result : dict[BiomassCategory | str, float]
        The rescaled category cover dict.
    """
    total_cover = sum(category_cover.values())
    return (
        _fill_category_cover(category_cover) if total_cover < _TARGET_LAND_COVER
        else _squash_category_cover(category_cover) if total_cover > _TARGET_LAND_COVER
        else category_cover
    )


def _fill_category_cover(
    category_cover:  dict[Union[BiomassCategory, str], float]
) -> dict[Union[BiomassCategory, str], float]:
    """
    Fill the land cover coverage with `BiomassCategory.OTHER` to enforce a total coverage of 100%.

    Parameters
    ----------
    category_cover : dict[BiomassCategory | str, float]
        The input category cover dict.

    Returns
    -------
    result : dict[BiomassCategory | str, float]
        The rescaled category cover dict.
    """
    total_cover = sum(category_cover.values())
    update_dict = {
        BiomassCategory.OTHER: category_cover.get(BiomassCategory.OTHER, 0) + (_TARGET_LAND_COVER - total_cover)
    }
    return category_cover | update_dict


def _squash_category_cover(
    category_cover: dict[Union[BiomassCategory, str], float]
) -> dict[Union[BiomassCategory, str], float]:
    """
    Proportionally shrink all land cover categories to enforce a total coverage of 100%.

    Parameters
    ----------
    category_cover : dict[BiomassCategory | str, float]
        The input category cover dict.

    Returns
    -------
    result : dict[BiomassCategory | str, float]
        The rescaled category cover dict.
    """
    total_cover = sum(category_cover.values())
    return {
        category: (cover / total_cover) * _TARGET_LAND_COVER
        for category, cover in category_cover.items()
    }


def detect_land_cover_change(
    a: dict[Union[BiomassCategory, str], float],
    b: dict[Union[BiomassCategory, str], float]
) -> bool:
    """
    Land cover values (% area) are compared with an absolute tolerance of 0.0001, which is equivalent to 1 m2 per
    hectare.

    Parameters
    ----------
    a : dict[BiomassCategory | str, float]
        The first land-cover summary dict.
    b : dict[BiomassCategory | str, float]
        The second land-cover summary dict.

    Returns
    -------
    bool
        Whether a land-cover change event has occured.
    """
    keys_match = sorted(str(key) for key in b.keys()) == sorted(str(key) for key in a.keys())
    values_close = all(
        isclose(b.get(key), a.get(key, -999), abs_tol=0.0001) for key in b.keys()
    )

    return not all([keys_match, values_close])


def _assign_biomass_category(lookup_value: str) -> BiomassCategory:
    """
    Return the `BiomassCategory` enum member associated with the input lookup value. If lookup value is missing or
    doesn't map to any category, return `None`.
    """
    return next(
        (key for key, value in _BIOMASS_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE.items() if value == lookup_value),
        None
    )


def sample_biomass_equilibrium(
    iterations: int,
    biomass_category: BiomassCategory,
    eco_climate_zone: EcoClimateZone,
    build_col_name_func: Callable[[BiomassCategory], str],
    seed: Union[int, random.Generator, None] = None
) -> dict:
    """
    Sample a biomass equilibrium using the function specified in `KWARGS_TO_SAMPLE_FUNC`.

    Parameters
    ----------
    iterations : int
        The number of samples to take.
    biomass_category : BiomassCategory
        The biomass category of the land cover.
    eco_climate_zone : EcoClimateZone
        The eco-climate zone of the site.
    build_col_name_func : Callable[[BiomassCategory], str]
        Function to build the name of the lookup column for a biomass category stock.
    seed : int | Generator | None, optional
        A seed to initialize the BitGenerator. If passed a Generator, it will be returned unaltered. If `None`, then
        fresh, unpredictable entropy will be pulled from the OS.

    Returns
    -------
    NDArray
        The sampled parameter as a numpy array with shape `(1, iterations)`.
    """
    DEFAULT_LOOKUP_DATA = {"value": 0}
    col_name = build_col_name_func(biomass_category)
    kwargs = get_ecoClimateZone_lookup_grouped_value(eco_climate_zone.value, col_name, default=DEFAULT_LOOKUP_DATA)
    func = _get_sample_func(kwargs)
    return func(iterations=iterations, seed=seed, **kwargs)


def _get_sample_func(kwargs: dict) -> Callable:
    """
    Select the correct sample function for a parameter based on the distribution data available. All possible
    parameters for the model should have, at a minimum, a `value`, meaning that no default function needs to be
    specified.

    This function has been extracted into it's own method to allow for mocking of sample function.

    Keyword Args
    ------------
    value : float
        The distribution mean.
    sd : float
        The standard deviation of the distribution.
    uncertainty : float
        The +/- uncertainty of the 95% confidence interval expressed as a percentage of the mean.
    error : float
        Two standard deviations expressed as a percentage of the mean.

    Returns
    -------
    Callable
        The sample function for the distribution.
    """
    return next(
        sample_func for required_kwargs, sample_func in _KWARGS_TO_SAMPLE_FUNC.items()
        if all(kwarg in kwargs.keys() for kwarg in required_kwargs)
    )


def sample_plus_minus_error(
    *, iterations: int, value: float, error: float, seed: Optional[int] = None, **_
) -> NDArray:
    """Randomly sample a model parameter with a truncated normal distribution described using plus/minus error."""
    sd = value * (error / 200)
    return truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sd, low=0, high=inf, seed=seed)


def sample_constant(*, iterations: int, value: float, **_) -> NDArray:
    """Sample a constant model parameter."""
    return repeat_single(shape=(1, iterations), value=value)


_KWARGS_TO_SAMPLE_FUNC = {
    ("value", "error"): sample_plus_minus_error,
    ("value",): sample_constant
}


def get_valid_management_nodes(site: dict) -> list[dict]:
    """Retrieve valid `landCover` nodes from a site's management."""
    COVER_CROP_TERM_IDS = get_cover_crop_property_terms()
    return [
        node for node in filter_list_term_type(site.get("management", []), TermTermType.LANDCOVER)
        if (
            validate_start_date_end_date(node)
            and not any(
                prop.get("value", False) for prop in node.get("properties", [])
                if node_term_match(prop, COVER_CROP_TERM_IDS)
            )
        )
    ]
