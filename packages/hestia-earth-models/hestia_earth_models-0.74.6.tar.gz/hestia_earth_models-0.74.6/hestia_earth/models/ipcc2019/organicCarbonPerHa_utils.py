from enum import Enum
from numpy import inf
from numpy.typing import NDArray
from typing import NamedTuple, Optional
from hestia_earth.schema import MeasurementStatsDefinition, SiteSiteType
from hestia_earth.utils.stats import calc_z_critical

from hestia_earth.utils.stats import (
    repeat_single, truncated_normal_1d
)
from hestia_earth.models.utils.blank_node import cumulative_nodes_term_match, node_term_match
from hestia_earth.models.utils.term import get_cover_crop_property_terms, get_irrigated_terms

STATS_DEFINITION = MeasurementStatsDefinition.SIMULATED.value
DEPTH_UPPER = 0
DEPTH_LOWER = 30

MIN_AREA_THRESHOLD = 30  # 30% as per IPCC guidelines
SUPER_MAJORITY_AREA_THRESHOLD = 100 - MIN_AREA_THRESHOLD
MIN_YIELD_THRESHOLD = 1


class IpccSoilCategory(Enum):
    """
    Enum representing IPCC Soil Categories.

    See [IPCC (2019) Vol 4, Ch. 2 and 3](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more
    information.
    """
    ORGANIC_SOILS = "organic soils"
    SANDY_SOILS = "sandy soils"
    WETLAND_SOILS = "wetland soils"
    VOLCANIC_SOILS = "volcanic soils"
    SPODIC_SOILS = "spodic soils"
    HIGH_ACTIVITY_CLAY_SOILS = "high-activity clay soils"
    LOW_ACTIVITY_CLAY_SOILS = "low-activity clay soils"


IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_LOOKUP_VALUE = {
    IpccSoilCategory.ORGANIC_SOILS: "Organic soils",
    IpccSoilCategory.SANDY_SOILS: "Sandy soils",
    IpccSoilCategory.WETLAND_SOILS: "Wetland soils",
    IpccSoilCategory.VOLCANIC_SOILS: "Volcanic soils",
    IpccSoilCategory.SPODIC_SOILS: "Spodic soils",
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: "High-activity clay soils",
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: "Low-activity clay soils",
}
"""
A dictionary mapping IPCC soil categories to corresponding soil type and USDA soil type lookup values in the
`"IPCC_SOIL_CATEGORY"` column.
"""


class IpccLandUseCategory(Enum):
    """
    Enum representing IPCC Land Use Categories.

    See [IPCC (2019) Vol 4](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.
    """
    GRASSLAND = "grassland"
    PERENNIAL_CROPS = "perennial crops"
    PADDY_RICE_CULTIVATION = "paddy rice cultivation"
    ANNUAL_CROPS_WET = "annual crops (wet)"
    ANNUAL_CROPS = "annual crops"
    SET_ASIDE = "set aside"
    FOREST = "forest"
    NATIVE = "native"
    OTHER = "other"
    UNKNOWN = "unknown"


SITE_TYPE_TO_IPCC_LAND_USE_CATEGORY = {
    SiteSiteType.PERMANENT_PASTURE.value: IpccLandUseCategory.GRASSLAND,
    SiteSiteType.FOREST.value: IpccLandUseCategory.FOREST,
    SiteSiteType.OTHER_NATURAL_VEGETATION.value: IpccLandUseCategory.NATIVE
}
"""
A dictionary mapping site types to corresponding IPCC land use categories.
"""

IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE = {
    IpccLandUseCategory.GRASSLAND: "Grassland",
    IpccLandUseCategory.PERENNIAL_CROPS: "Perennial crops",
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: "Paddy rice cultivation",
    IpccLandUseCategory.ANNUAL_CROPS_WET: "Annual crops",
    IpccLandUseCategory.ANNUAL_CROPS: "Annual crops",
    IpccLandUseCategory.SET_ASIDE: "Set aside",
    IpccLandUseCategory.FOREST: "Forest",
    IpccLandUseCategory.NATIVE: "Native",
    IpccLandUseCategory.OTHER: "Other"
}
"""
A dictionary mapping IPCC land use categories to corresponding land cover lookup values in the
`"IPCC_LAND_USE_CATEGORY"` column.
"""


class IpccManagementCategory(Enum):
    """
    Enum representing IPCC Management Categories for grasslands and annual croplands.

    See [IPCC (2019) Vol. 4, Ch. 5 and 6](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more
    information.
    """
    SEVERELY_DEGRADED = "severely degraded"
    IMPROVED_GRASSLAND = "improved grassland"
    HIGH_INTENSITY_GRAZING = "high-intensity grazing"
    NOMINALLY_MANAGED = "nominally managed"
    FULL_TILLAGE = "full tillage"
    REDUCED_TILLAGE = "reduced tillage"
    NO_TILLAGE = "no tillage"
    UNKNOWN = "unknown"
    NOT_RELEVANT = "not relevant"


IPCC_MANAGEMENT_CATEGORY_TO_GRASSLAND_MANAGEMENT_TERM_ID = {
    IpccManagementCategory.SEVERELY_DEGRADED: "severelyDegradedPasture",
    IpccManagementCategory.IMPROVED_GRASSLAND: "improvedPasture",
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: "highIntensityGrazingPasture",
    IpccManagementCategory.NOMINALLY_MANAGED: ["nominallyManagedPasture", "nativePasture"]
}
"""
A dictionary mapping IPCC management categories to corresponding grassland management term IDs from the land cover
glossary.
"""


IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE = {
    IpccManagementCategory.FULL_TILLAGE: "Full tillage",
    IpccManagementCategory.REDUCED_TILLAGE: "Reduced tillage",
    IpccManagementCategory.NO_TILLAGE: "No tillage"
}
"""
A dictionary mapping IPCC management categories to corresponding tillage lookup values in the
`"IPCC_TILLAGE_MANAGEMENT_CATEGORY" column`.
"""


class IpccCarbonInputCategory(Enum):
    """
    Enum representing IPCC Carbon Input Categories for improved grasslands and annual croplands.

    See [IPCC (2019) Vol. 4, Ch. 4, 5 and 6](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more
    information.
    """
    GRASSLAND_HIGH = "grassland high"
    GRASSLAND_MEDIUM = "grassland medium"
    CROPLAND_HIGH_WITH_MANURE = "cropland high (with manure)"
    CROPLAND_HIGH_WITHOUT_MANURE = "cropland high (without manure)"
    CROPLAND_MEDIUM = "cropland medium"
    CROPLAND_LOW = "cropland low"
    UNKNOWN = "unknown"
    NOT_RELEVANT = "not relevant"


CarbonSource = NamedTuple(
    "CarbonSource",
    [
        ("mass", float),
        ("carbon_content", float),
        ("nitrogen_content", float),
        ("lignin_content", float),
    ]
)
"""
A single carbon source (e.g. crop residues or organic amendment).

Attributes
-----------
mass : float
    The dry-matter mass of the carbon source, kg ha-1
carbon_content : float
    The carbon content of the carbon source, decimal proportion, kg C (kg d.m.)-1.
nitrogen_content : float
    The nitrogen content of the carbon source, decimal_proportion, kg N (kg d.m.)-1.
lignin_content : float
    The lignin content of the carbon source, decimal_proportion, kg lignin (kg d.m.)-1.
"""


def check_consecutive(ints: list[int]) -> bool:
    """
    Checks whether a list of integers are consecutive.

    Used to determine whether annualised data is complete from every year from beggining to end.

    Parameters
    ----------
    ints : list[int]
        A list of integer values.

    Returns
    -------
    bool
        Whether or not the list of integers is consecutive.
    """
    range_list = list(range(min(ints), max(ints)+1)) if ints else []
    return all(a == b for a, b in zip(ints, range_list))


def check_irrigation(water_regime_nodes: list[dict]) -> bool:
    """
    Check if irrigation is present in the water regime nodes.

    Parameters
    ----------
    water_regime_nodes : list[dict]
        List of water regime nodes to be checked.

    Returns
    -------
    bool
        `True` if irrigation is present, `False` otherwise.
    """
    return cumulative_nodes_term_match(
        water_regime_nodes,
        target_term_ids=get_irrigated_terms(),
        cumulative_threshold=MIN_AREA_THRESHOLD
    )


def is_cover_crop(node: dict) -> bool:
    """Check if a `landCover` node represents a cover crop."""
    COVER_CROP_TERM_IDS = get_cover_crop_property_terms()
    return any(
        prop.get("value", False) for prop in node.get("properties", [])
        if node_term_match(prop, COVER_CROP_TERM_IDS)
    )


def sample_truncated_normal(
    *, iterations: int, value: float, sd: float, min: float, max: float, seed: Optional[int] = None, **_
) -> NDArray:
    """Randomly sample a model parameter with a truncated normal distribution."""
    return truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sd, low=min, high=max, seed=seed)


def sample_plus_minus_uncertainty(
    *, iterations: int, value: float, uncertainty: float, seed: Optional[int] = None, **_
) -> NDArray:
    """Randomly sample a model parameter with a plus/minus uncertainty distribution."""
    n_sds = calc_z_critical(95)
    sigma = (value * (uncertainty / 100)) / n_sds
    return truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sigma, low=0, high=inf, seed=seed)


def sample_plus_minus_error(
    *, iterations: int, value: float, error: float, seed: Optional[int] = None, **_
) -> NDArray:
    """Randomly sample a model parameter with a truncated normal distribution described using plus/minus error."""
    sd = value * (error / 200)
    return truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sd, low=0, high=inf, seed=seed)


def sample_constant(*, iterations: int, value: float, **_) -> NDArray:
    """Sample a constant model parameter."""
    return repeat_single(shape=(1, iterations), value=value)


def format_bool(value: Optional[bool]) -> str:
    """Format a bool for logging in a table."""
    return str(bool(value))


def format_number(value: Optional[float]) -> str:
    """Format a float for logging in a table."""
    return f"{value:.1f}" if isinstance(value, (float, int)) else "None"


def format_enum(value: Optional[Enum]) -> str:
    """Format an enum for logging in a table."""
    return value.value if isinstance(value, Enum) else "None"


def format_bool_list(values: Optional[list[bool]]) -> str:
    """Format a list of bools for logging in a table."""
    return (
        " ".join(format_bool(value) for value in values) or "None" if isinstance(values, list)
        else "None"
    )


def format_number_list(values: Optional[list[float]]) -> str:
    """Format a list of floats for logging in a table."""
    return (
        " ".join(format_number(value) for value in values) or "None"if isinstance(values, list)
        else "None"
    )
