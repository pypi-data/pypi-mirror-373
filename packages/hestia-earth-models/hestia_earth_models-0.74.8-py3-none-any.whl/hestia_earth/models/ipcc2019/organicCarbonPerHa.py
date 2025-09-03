from functools import reduce
from pydash.objects import merge
from types import ModuleType

from hestia_earth.models.log import log_as_table, logRequirements, logShouldRun

from .organicCarbonPerHa_utils import format_bool, format_bool_list, format_enum, format_number, format_number_list
from . import organicCarbonPerHa_tier_1 as tier_1
from . import organicCarbonPerHa_tier_2 as tier_2
from . import MODEL  # noqa

REQUIREMENTS = {
    "Site": {
        "management": [
            {"@type": "Management", "value": "", "term.termType": "landCover"}
        ],
        "measurements": [
            {
                "@type": "Measurement",
                "value": ["1", "2", "3", "4", "7", "8", "9", "10", "11", "12"],
                "term.@id": "ecoClimateZone"
            }
        ],
        "optional": {
            "measurements": [
                {"@type": "Measurement", "value": "", "term.termType": ["soilType", "usdaSoilType"]}
            ],
            "management": [
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "cropResidueManagement",
                    "name": ["burnt", "removed"]
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "landUseManagement"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.termType": "tillage"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "waterRegime",
                    "name": ["deep water", "irrigated"]
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "amendmentIncreasingSoilCarbonUsed"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "animalManureUsed"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "inorganicNitrogenFertiliserUsed"
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "organicFertiliserUsed"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "shortBareFallow"}
            ]
        },
        "none": {
            "siteType": ["glass or high accessible cover"]
        }
    }
}
LOOKUPS = {
    "crop": "IPCC_LAND_USE_CATEGORY",
    "landCover": [
        "IPCC_LAND_USE_CATEGORY",
        "LOW_RESIDUE_PRODUCING_CROP",
        "N_FIXING_CROP"
    ],
    "landUseManagement": "PRACTICE_INCREASING_C_INPUT",
    "soilType": "IPCC_SOIL_CATEGORY",
    "tillage": "IPCC_TILLAGE_MANAGEMENT_CATEGORY",
    "usdaSoilType": "IPCC_SOIL_CATEGORY"
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "statsDefinition": "simulated",
        "observations": "",
        "dates": "",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": ""
    }]
}
TERM_ID = 'organicCarbonPerHa'
ITERATIONS = 10000  # TODO: Refine number of iterations to balance performance and precision.

_METHOD_TIERS = [tier_2, tier_1]


def run(site: dict) -> list[dict]:
    """
    Run both tiers of the IPCC (2019) SOC model.

    Parameters
    ----------
    site : dict
        A HESTIA `Site` node, see: https://www.hestia.earth/schema/Site.

    Returns
    -------
    list[dict]
        A list of HESTIA `Measurement` nodes containing the calculated SOC stocks and additional relevant data.
    """
    should_run, run_data = _should_run(site)
    _log_data(site, should_run, run_data)
    return reduce(
        lambda result, method: result + _run_method(method, **run_data[method]),
        run_data,
        list()
    )


def _should_run(site: dict) -> tuple[bool, dict[ModuleType, dict]]:
    # List of tuples `(should_run, inventory, kwargs, logs)` for each method tier.
    INNER_KEYS = ("should_run", "inventory", "kwargs", "logs")
    run_data = {
        method: {
            key: value for key, value in zip(INNER_KEYS, method.should_run(site))
        } for method in _METHOD_TIERS
    }
    should_run = any(data["should_run"] for data in run_data.values())
    return should_run, run_data


def _log_data(site: dict, should_run: bool, run_data: dict[ModuleType, dict]) -> None:
    """
    Format and log the inventory, kwargs and any other requirement data for all tier methodologies of the model.
    """
    inventory = reduce(merge, [data["inventory"] for data in run_data.values()], dict())
    kwargs = reduce(merge, [data["kwargs"] for data in run_data.values()], dict())
    logs = reduce(merge, [data["logs"] for data in run_data.values()], dict())

    logRequirements(
        site,
        model=MODEL,
        term=TERM_ID,
        **logs,
        **kwargs,
        inventory=_format_inventory(inventory)
    )
    logShouldRun(site, MODEL, TERM_ID, should_run)


def _format_inventory(inventory: dict) -> str:
    """
    Format the inventory as a table.
    """
    inventory_keys = _get_unique_inventory_keys(inventory)
    return log_as_table(
        {
            "year": year,
            **{
                key.value: _INVENTORY_KEY_TO_FORMAT_FUNC[key](group.get(key))
                for key in inventory_keys
            }
        } for year, group in inventory.items()
    ) if inventory else "None"


def _get_unique_inventory_keys(inventory: dict) -> list:
    """
    Return a list of unique inventory keys in a fixed order.
    """
    unique_keys = reduce(
        lambda result, keys: result | set(keys),
        (
            (key for key in group.keys() if key in _INVENTORY_KEY_TO_FORMAT_FUNC)
            for group in inventory.values()
        ),
        set()
    )
    key_order = {key: i for i, key in enumerate(_INVENTORY_KEY_TO_FORMAT_FUNC.keys())}
    return sorted(unique_keys, key=lambda key_: key_order[key_])


_INVENTORY_KEY_TO_FORMAT_FUNC = {
    tier_2._InventoryKey.SHOULD_RUN: format_bool,
    tier_2._InventoryKey.TEMP_MONTHLY: format_number_list,
    tier_2._InventoryKey.PRECIP_MONTHLY: format_number_list,
    tier_2._InventoryKey.PET_MONTHLY: format_number_list,
    tier_2._InventoryKey.IRRIGATED_MONTHLY: format_bool_list,
    tier_2._InventoryKey.SAND_CONTENT: format_number,
    tier_2._InventoryKey.CARBON_INPUT: format_number,
    tier_2._InventoryKey.N_CONTENT: format_number,
    tier_2._InventoryKey.LIGNIN_CONTENT: format_number,
    tier_2._InventoryKey.TILLAGE_CATEGORY: format_enum,
    tier_2._InventoryKey.IS_PADDY_RICE: format_bool,
    tier_1._InventoryKey.SHOULD_RUN: format_bool,
    tier_1._InventoryKey.LU_CATEGORY: format_enum,
    tier_1._InventoryKey.MG_CATEGORY: format_enum,
    tier_1._InventoryKey.CI_CATEGORY: format_enum,
}
"""
Map inventory keys to format functions. The columns in inventory logged as a table will also be sorted in the order of
the `dict` keys.
"""


def _run_method(method: ModuleType, should_run: bool, inventory: dict, kwargs: dict, **_) -> list[dict]:
    return method.run(inventory, **kwargs, iterations=ITERATIONS) if should_run else []
