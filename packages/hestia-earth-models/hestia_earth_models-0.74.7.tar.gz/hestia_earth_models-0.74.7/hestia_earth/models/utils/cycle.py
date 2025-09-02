from hestia_earth.schema import CycleFunctionalUnit, SiteSiteType, TermTermType, AnimalReferencePeriod
from hestia_earth.utils.model import filter_list_term_type, find_term_match, find_primary_product
from hestia_earth.utils.tools import list_sum, safe_parse_float, safe_parse_date, non_empty_list
from hestia_earth.utils.lookup_utils import is_siteType_allowed

from ..log import logRequirements, debugValues
from .lookup import all_factor_value
from .term import get_lookup_value
from .property import get_node_property
from .completeness import _is_term_type_complete
from .blank_node import get_N_total, get_P2O5_total
from .measurement import most_relevant_measurement_value
from .crop import is_plantation
from .currency import DEFAULT_CURRENCY
from .inorganicFertiliser import get_cycle_inputs as get_inorganicFertiliser_inputs
from .organicFertiliser import get_cycle_inputs as get_organicFertiliser_inputs


def unique_currencies(cycle: dict) -> list:
    """
    Get the list of different currencies used in the Cycle.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    list
        The list of currencies as string.
    """
    products = cycle.get('products', [])
    return list(set([p.get('currency') for p in products if p.get('currency') is not None]))


def default_currency(cycle: dict) -> str:
    """
    Get the default currency for the Cycle.
    If multiple curriencies are used, will default to `USD`.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    str
        The default currency.
    """
    currencies = unique_currencies(cycle)
    return currencies[0] if len(currencies) == 1 else DEFAULT_CURRENCY


def get_crop_residue_decomposition_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of `cropResidue` decomposed.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROPRESIDUE)
    # filter products matching lookup `decomposesOnField`
    products = [
        p for p in products if get_lookup_value(p.get('term'), 'decomposesOnField')
    ]
    default_value = 0 if _is_term_type_complete(cycle, TermTermType.CROPRESIDUE) else None
    return list_sum(get_N_total(products), default_value)


def get_excreta_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of excreta used in the Cycle.

    The result is the sum of every excreta specified in `kg N` as an `Input` or a `Product`.

    Note: in the event where `completeness.product` is set to `True` and there are no excreta inputs or products,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.EXCRETA)
    products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    values = get_N_total(inputs) + get_N_total(products)
    default_value = 0 if _is_term_type_complete(cycle, TermTermType.EXCRETA) else None
    return list_sum(values, default_value)


def get_organic_fertiliser_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of organic fertilisers used in the Cycle.

    The result contains the values of the following `Input`s:
    1. Every organic fertiliser specified in `kg N` will be used.
    2. Every organic fertiliser specified in `kg` will be multiplied by the `nitrogenContent` of that fertiliser.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no organic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    values = get_N_total(get_organicFertiliser_inputs(cycle))
    default_value = 0 if _is_term_type_complete(cycle, 'fertiliser') else None
    return list_sum(values, default_value)


def get_organic_fertiliser_P_total(cycle: dict) -> float:
    """
    Get the total phosphate content of organic fertilisers used in the Cycle.

    The result contains the values of the following `Input`s:
    1. Every organic fertiliser specified in `kg P2O5` will be used.
    2. Every organic fertiliser specified in `kg` will be multiplied by the `nitrogenContent` of that fertiliser.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no organic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    values = get_P2O5_total(get_organicFertiliser_inputs(cycle))
    default_value = 0 if _is_term_type_complete(cycle, 'fertiliser') else None
    return list_sum(values, default_value)


def get_inorganic_fertiliser_N_total(cycle: dict) -> float:
    """
    Get the total nitrogen content of inorganic fertilisers used in the Cycle.

    The result is the sum of every inorganic fertiliser specified in `kg N` as an `Input`.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no inorganic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    values = get_N_total(get_inorganicFertiliser_inputs(cycle))
    default_value = 0 if _is_term_type_complete(cycle, 'fertiliser') else None
    return list_sum(values, default_value)


def get_inorganic_fertiliser_P_total(cycle: dict) -> float:
    """
    Get the total Phosphate content of inorganic fertilisers used in the Cycle.

    The result is the sum of every inorganic fertiliser specified in `kg P2O5` as an `Input`.

    Note: in the event where `completeness.fertiliser` is set to `True` and there are no inorganic fertilisers used,
    `0` will be returned.

    Parameters
    ----------
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    float
        The total value as a number.
    """
    values = get_P2O5_total(get_inorganicFertiliser_inputs(cycle))
    default_value = 0 if _is_term_type_complete(cycle, 'fertiliser') else None
    return list_sum(values, default_value)


def get_max_rooting_depth(cycle: dict) -> float:
    properties = list(map(lambda p: get_node_property(p, 'rootingDepth'), cycle.get('products', [])))
    values = [safe_parse_float(p.get('value'), default=0) for p in properties if p.get('value') is not None]
    return max(values) if len(values) > 0 else None


def _land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    cycleDuration = cycle.get('cycleDuration', 365)
    longFallowRatio = find_term_match(cycle.get('practices', []), 'longFallowRatio')
    longFallowRatio = longFallowRatio.get('value', [None])[0]
    value = cycleDuration / 365 * longFallowRatio if longFallowRatio is not None else None

    logRequirements(cycle, model=model, term=term_id,
                    cycleDuration=cycleDuration,
                    longFallowRatio=longFallowRatio,
                    value_per_ha=value)

    return value


def _plantation_land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    practices = cycle.get('practices', [])
    nurseryDuration = list_sum(find_term_match(practices, 'nurseryDuration').get('value', []), None)
    plantationProductiveLifespan = list_sum(
        find_term_match(practices, 'plantationProductiveLifespan').get('value', []), None)
    plantationDensity = list_sum(find_term_match(practices, 'plantationDensity').get('value', []), None)
    plantationLifespan = list_sum(find_term_match(practices, 'plantationLifespan').get('value', []), None)
    rotationDuration = list_sum(find_term_match(practices, 'rotationDuration').get('value', []), None)
    nurseryDensity = list_sum(find_term_match(practices, 'nurseryDensity').get('value', []), None)

    logRequirements(cycle, model=model, term=term_id,
                    nurseryDuration=nurseryDuration,
                    nurseryDensity=nurseryDensity,
                    plantationDensity=plantationDensity,
                    plantationLifespan=plantationLifespan,
                    plantationProductiveLifespan=plantationProductiveLifespan,
                    rotationDuration=rotationDuration)

    should_run = all([
        nurseryDuration, nurseryDensity,
        plantationDensity, plantationLifespan, plantationProductiveLifespan,
        rotationDuration
    ])
    return (plantationLifespan/plantationProductiveLifespan) * (
        1 + (nurseryDuration/365)/nurseryDensity * plantationDensity/(plantationLifespan/365)  # nursery
    ) * rotationDuration/plantationLifespan if should_run else None


def land_occupation_per_ha(model: str, term_id: str, cycle: dict):
    """
    Get the land occupation of the cycle per hectare in hectare.

    Parameters
    ----------
    model : str
        The name of the model running this function. For debugging purpose only.
    term_id : str
        The name of the term running this function. For debugging purpose only.
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.

    Returns
    -------
    float
        The land occupation in hectare.
    """
    product = find_primary_product(cycle) or {}
    plantation = is_plantation(model, term_id, product.get('term', {}).get('@id'))
    return _plantation_land_occupation_per_ha(model, term_id, cycle) if plantation \
        else _land_occupation_per_ha(model, term_id, cycle)


def _land_occupation_per_kg(model: str, term_id: str, cycle: dict, product: dict, land_occupation_per_ha: float):
    functionalUnit = cycle.get('functionalUnit')
    product_value = list_sum(product.get('value', [0]))
    economicValueShare = product.get('economicValueShare', 0)

    value = land_occupation_per_ha * 10000 * (economicValueShare / 100)
    value = value / product_value if all([product_value > 0, economicValueShare > 0]) else None
    value = value if functionalUnit == CycleFunctionalUnit._1_HA.value else None

    logRequirements(cycle, model=model, term=term_id,
                    functionalUnit=functionalUnit,
                    product_yield=product_value,
                    economicValueShare=economicValueShare,
                    value_per_kg_per_m2=value)

    return value


def land_occupation_per_kg(model: str, term_id: str, cycle: dict, site: dict, product: dict):
    """
    Get the land occupation of the cycle per kg in meter square.

    Parameters
    ----------
    model : str
        The name of the model running this function. For debugging purpose only.
    term_id : str
        The name of the term running this function. For debugging purpose only.
    cycle : dict
        The `Cycle` as defined in the HESTIA Schema.
    site : dict
        The `Site` as defined in the HESTIA Schema.
    product : dict
        The primary `Product` of the `Cycle`.

    Returns
    -------
    float
        The land occupation in m2.
    """
    site_type = site.get('siteType')
    value = land_occupation_per_ha(model, term_id, cycle)
    return 0 if site_type in [
        # assume the land occupation is 0 for these sites
        SiteSiteType.AGRI_FOOD_PROCESSOR.value,
        SiteSiteType.ANIMAL_HOUSING.value,
        SiteSiteType.FOOD_RETAILER.value,
        SiteSiteType.LAKE.value,
        SiteSiteType.POND.value,
        SiteSiteType.RIVER_OR_STREAM.value,
        SiteSiteType.SEA_OR_OCEAN.value
    ] else (
        _land_occupation_per_kg(model, term_id, cycle, product, value) if value is not None else None
    )


def is_organic(cycle: dict):
    """
    Check if the `Cycle` is organic, i.e. if it contains an organic standard label `Practice`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    bool
        `True` if the `Cycle` is organic, `False` otherwise.
    """
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.STANDARDSLABELS)
    return next((get_lookup_value(p.get('term', {}), 'isOrganic') == 'organic' for p in practices), False)


def is_irrigated(cycle: dict, **log_ars):
    """
    Check if the `Cycle` is irrigated, i.e. if it contains an irrigated `Practice` with a value above `0`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.
    log_ars : dict[str, Any]
        Extra loggging, e.g. model, term.

    Returns
    -------
    bool
        `True` if the `Cycle` is irrigated, `False` otherwise.
    """
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.WATERREGIME)
    irrigated_practices = [p for p in practices if get_lookup_value(p.get('term', {}), 'irrigated', **log_ars)]
    return any([list_sum(p.get('value', []), 0) > 0 for p in irrigated_practices])


def cycle_end_year(cycle: dict):
    """
    End year of the `Cycle`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.

    Returns
    -------
    number
        The year in which the `Cycle` ends.
    """
    date = safe_parse_date(cycle.get('endDate'))
    return date.year if date else None


def impact_lookup_value(model: str, term_id: str, cycle: dict, blank_nodes: list, lookup_col: str) -> float:
    """
    Calculate the value of the impact based on lookup factors and cycle values.

    Parameters
    ----------
    term_id : str
        The term to display in the logs only.
    blank_nodes : list
        The list of blank nodes from the Cycle.
    lookup_col : str
        The lookup column to fetch the factors from.
    allow_missing : bool
        Allow missing factors. Default to `False` (will return `None` if one factor is missing).

    Returns
    -------
    int
        The impact total value.
    """
    term_type = blank_nodes[0].get('term', {}).get('termType') if len(blank_nodes) > 0 else None
    return all_factor_value(
        log_model=model,
        log_term_id=term_id,
        log_node=cycle,
        lookup_name=f"{term_type}.csv",
        lookup_col=lookup_col,
        blank_nodes=blank_nodes
    )


def get_ecoClimateZone(cycle: dict) -> int:
    """
    Get the `ecoClimateZone` value from the Site Measurements (if present).

    Parameters
    ----------
    cycle : dict
        The full Cycle containing the Site.

    Returns
    -------
    int
        The ecoClimateZone value from 1 to 12.
    """
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    return most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)


def check_cycle_site_ids_identical(cycles: list[dict]) -> bool:
    """
    Checks whether the sites of a list of cycles are the same.

    Parameters
    ----------
    cycles : list[dict]
        A list of HESTIA `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    bool
        Whether or not all of the cycles associated site ids are identical.
    """
    return len(set(cycle.get('site', {}).get('@id', None) for cycle in cycles)) <= 1


def get_animals_by_period(cycle: dict, period: AnimalReferencePeriod = AnimalReferencePeriod.AVERAGE):
    return [
        a for a in cycle.get('animals', []) if all([
            a.get('value'),
            a.get('referencePeriod') == period.value
        ])
    ]


def get_allowed_sites(model: str, term_id: str, cycle: dict):
    sites = non_empty_list([cycle.get('site', None)]) + cycle.get('otherSites', [])
    allowed_sites = [s for s in sites if is_siteType_allowed(s, term_id)]
    allowed_site_ids = non_empty_list([s.get('@id', s.get('id')) for s in allowed_sites])
    debugValues(cycle, model=model, term=term_id, site_ids=';'.join(allowed_site_ids))
    return allowed_sites
