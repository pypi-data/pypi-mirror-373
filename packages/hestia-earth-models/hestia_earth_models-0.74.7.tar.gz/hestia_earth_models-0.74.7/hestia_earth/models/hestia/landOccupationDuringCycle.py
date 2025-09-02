from functools import reduce
from itertools import zip_longest
from typing import NamedTuple

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table

from hestia_earth.models.utils import hectar_to_square_meter
from hestia_earth.models.utils.constant import DAYS_IN_YEAR
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product
from hestia_earth.models.utils.site import get_land_cover_term_id as get_landCover_term_id_from_site_type
from hestia_earth.models.utils.crop import get_landCover_term_id
from hestia_earth.schema import CycleFunctionalUnit

from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "product": {
            "@type": "Term",
            "value": "> 0",
            "optional": {
                "@doc": "if the [cycle.functionalUnit](https://hestia.earth/schema/Cycle#functionalUnit) = 1 ha, additional properties are required",  # noqa: E501
                "economicValueShare": ">= 0"
            }
        },
        "cycle": {
            "@type": "Cycle",
            "site": {
                "@type": "Site",
                "country": {"@type": "Term", "termType": "region"}
            },
            "siteArea": ">= 0",
            "siteDuration": ">= 0",
            "siteUnusedDuration": ">= 0",
            "optional": {
                "@doc": "When `otherSites` are provided, `otherSitesArea`, `otherSitesDuration` and `otherSitesUnusedDuration` are required",  # noqa: E501
                "otherSites": [{
                    "@type": "Site",
                    "country": {"@type": "Term", "termType": "region"}
                }],
                "otherSitesArea": "",
                "otherSitesDuration": "",
                "otherSitesUnusedDuration": ""
            }
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "landCover": ""
    }]
}
TERM_ID = 'landOccupationDuringCycle'


class SiteData(NamedTuple):
    id: str  # site.@id
    area: float
    duration: float
    unused_duration: float
    land_cover_id: str
    country_id: str


def _indicator(term_id: str, value: float, land_cover_id: str, country_id: str):
    indicator = _new_indicator(
        term_id, model=MODEL, land_cover_id=land_cover_id, country_id=country_id
    )
    indicator['value'] = round(value, 6)
    return indicator


def _calc_land_occupation_m2_per_ha(
    site_area: float, site_duration: float, site_unused_duration: float
) -> float:
    """
    Parameters
    ----------
    site_area : float
        Area of the site in hectares.
    site_duration : float
        Site duration in days.
    site_unused_duration : float
        Site unused duration in days.

    Returns
    -------
    float
    """
    return hectar_to_square_meter(site_area) * (site_duration + site_unused_duration) / DAYS_IN_YEAR


def _calc_land_occupation_m2_per_kg(
    yield_: float, economic_value_share: float, land_occupation_m2_per_ha: float,
) -> float:
    """
    Parameters
    ----------
    yield_ : float
        Product yield in product units.
    economic_value_share : float
        Economic value share of the product in % (0-100).
    land_occupation_m2_per_ha : float
        Land occupation in m2 ha-1.

    Returns
    -------
    float
    """
    return land_occupation_m2_per_ha * economic_value_share * 0.01 / yield_


def _extract_site_data(cycle: dict, land_cover_id: dict):
    site = cycle.get("site", {})
    site_data = SiteData(
        id=site.get("@id"),
        area=cycle.get("siteArea"),
        duration=cycle.get("siteDuration"),
        unused_duration=cycle.get("siteUnusedDuration"),
        country_id=site.get("country", {}).get("@id"),
        land_cover_id=land_cover_id or get_landCover_term_id_from_site_type(site.get("siteType"))
    )

    is_valid = _should_run_site_data(site_data)

    logs = {
        "site_data": _format_inventory([site_data])
    }

    return is_valid, site_data, logs


def _extract_other_sites_data(cycle: dict, land_cover_id: dict):
    other_sites = cycle.get("otherSites", [])
    other_sites_area = cycle.get("otherSitesArea", [])
    other_sites_duration = cycle.get("otherSitesDuration", [])
    other_sites_unused_duration = cycle.get("otherSitesUnusedDuration", [])

    other_sites_data = [
        SiteData(
            id=site.get("@id"),
            area=area,
            duration=duration,
            unused_duration=unused_duration,
            country_id=site.get("country", {}).get("@id"),
            land_cover_id=land_cover_id or get_landCover_term_id_from_site_type(site.get("siteType"))
        ) for (
            site,
            area,
            duration,
            unused_duration
        ) in zip_longest(
            other_sites,
            other_sites_area,
            other_sites_duration,
            other_sites_unused_duration
        )
    ]

    is_valid = all(_should_run_site_data(other_site) for other_site in other_sites_data)

    logs = {
        "other_sites_count": len(other_sites),
        "other_sites_data": _format_inventory(other_sites_data, "Not relevant")
    }

    return is_valid, other_sites_data, logs


def _should_run_site_data(site_data: SiteData) -> bool:
    return all([
        site_data.area or site_data.area == 0,
        site_data.duration or site_data.duration == 0,
        site_data.unused_duration or site_data.unused_duration == 0,
        site_data.land_cover_id,
        site_data.country_id
    ])


def _format_float(value: float, unit: str = "", default: str = "None") -> str:
    return " ".join(
        string for string in [f"{value}", unit] if string
    ) if isinstance(value, (float, int)) else default


_INVALID_CHARS = {"_", ":", ",", "="}
_REPLACEMENT_CHAR = "-"


def _format_str(value: str, default: str = "None") -> str:
    """Format a string for logging in a table. Remove all characters used to render the table on the front end."""
    return (
        reduce(lambda x, char: x.replace(char, _REPLACEMENT_CHAR), _INVALID_CHARS, str(value))
        if value else default
    )


def _format_inventory(inventory: list[SiteData], default: str = "None") -> str:
    return log_as_table(
        {
            "site-id": _format_str(site_data.id),
            "site-area": _format_float(site_data.area, "ha"),
            "site-duration": _format_float(site_data.duration, "days"),
            "site-unused-duration": _format_float(site_data.unused_duration, "days"),
            "land-cover-id": _format_str(site_data.land_cover_id),
            "country-id": _format_str(site_data.country_id)
        } for site_data in inventory
    ) if inventory else default


def _should_run(impact_assessment: dict):

    cycle = impact_assessment.get("cycle")
    functional_unit = cycle.get("functionalUnit")

    product = get_product(impact_assessment)
    product_yield = sum(product.get("value", []))
    product_land_cover_id = get_landCover_term_id(product.get("term", {}), skip_debug=True)
    economic_value_share = (
        100 if functional_unit == CycleFunctionalUnit.RELATIVE.value
        else product.get("economicValueShare")
    )

    site_data_is_valid, site_data, site_logs = _extract_site_data(cycle, product_land_cover_id)
    (
        other_sites_data_is_valid,
        other_sites_data,
        other_sites_logs
    ) = _extract_other_sites_data(cycle, product_land_cover_id)

    inventory = [site_data] + other_sites_data

    valid_inventory = inventory and all(_should_run_site_data(site_data) for site_data in inventory)

    logRequirements(
        impact_assessment,
        model=MODEL,
        term=TERM_ID,
        functional_unit=functional_unit,
        product_yield=_format_float(product_yield, product.get("term", {}).get("units")),
        economic_value_share=_format_float(economic_value_share, "pct"),
        valid_inventory=valid_inventory,
        site_data_is_valid=site_data_is_valid,
        **site_logs,
        other_sites_data_is_valid=other_sites_data_is_valid,
        **other_sites_logs
    )

    should_run = all([
        product_yield > 0,
        economic_value_share or economic_value_share == 0,
        site_data_is_valid,
        other_sites_data_is_valid
    ])

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)

    return should_run, product_yield, economic_value_share, inventory


def _run(
    yield_: float,
    economic_value_share: float,
    inventory: list[SiteData]
) -> list[dict]:

    def calc_occupation_by_group(result: dict, site_data: SiteData):
        """Calculate the land occupation of a site and sum it with matching landCover/country groups."""

        land_occupation_m2_per_ha = _calc_land_occupation_m2_per_ha(
            site_data.area, site_data.duration, site_data.unused_duration
        )

        land_occupation_m2_per_kg = _calc_land_occupation_m2_per_kg(
            yield_, economic_value_share, land_occupation_m2_per_ha
        )

        key = (site_data.land_cover_id, site_data.country_id)
        return result | {key: result.get(key, 0) + land_occupation_m2_per_kg}

    land_occupation_by_group = reduce(calc_occupation_by_group, inventory, {})

    return [
        _indicator(TERM_ID, value, land_cover_id, country_id)
        for (land_cover_id, country_id), value in land_occupation_by_group.items()
    ]


def run(impact_assessment: dict):
    should_run, yield_, economic_value_share, inventory = _should_run(impact_assessment)
    return _run(yield_, economic_value_share, inventory) if should_run else []
