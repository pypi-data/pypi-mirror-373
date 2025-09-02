from functools import reduce
from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.date import DAY

from hestia_earth.models.utils import _omit, first_day_of_month, last_day_of_month
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.measurement import _new_measurement, measurement_value, has_all_months
from . import MODEL

IPCC_LAND_USE_CATEGORY_ANNUAL = "Annual crops"
IPCC_LAND_USE_CATEGORY_PERENNIAL = "Perennial crops"
TOTAL_CROPLAND = "Cropland"
ANNUAL_CROPLAND = "Arable land"
FOREST_LAND = "Forest land"
OTHER_LAND = "Other land"
PERMANENT_CROPLAND = "Permanent crops"
PERMANENT_PASTURE = "Permanent meadows and pastures"
TOTAL_AGRICULTURAL_CHANGE = "Total agricultural change"
ALL_LAND_USE_TERMS = [
    FOREST_LAND,
    TOTAL_CROPLAND,
    ANNUAL_CROPLAND,
    PERMANENT_CROPLAND,
    PERMANENT_PASTURE,
    OTHER_LAND
]

# Mapping from Land use terms to Management node terms.
# land use term: (@id, name)
LAND_USE_TERMS_FOR_TRANSFORMATION = {
    FOREST_LAND: ("forest", "Forest"),
    ANNUAL_CROPLAND: ("annualCropland", "Annual cropland"),
    PERMANENT_CROPLAND: ("permanentCropland", "Permanent cropland"),
    PERMANENT_PASTURE: ("permanentPasture", "Permanent pasture"),
    OTHER_LAND: ("otherLand", OTHER_LAND)  # Not used yet
}


def crop_ipcc_land_use_category(
    crop_term_id: str,
    lookup_term_type: str = TermTermType.LANDCOVER.value
) -> str:
    """
    Looks up the crop in the lookup.
    Returns the IPCC_LAND_USE_CATEGORY.
    """
    return get_lookup_value(
        lookup_term={"@id": crop_term_id, "type": "Term", "termType": lookup_term_type},
        column='IPCC_LAND_USE_CATEGORY',
        model=MODEL
    )


def get_liveAnimal_term_id(product: dict, **log_ars):
    term_id = get_lookup_value(product.get('term', {}), 'liveAnimalTermId', model=MODEL, **log_ars)
    return term_id.split(';')[0] if term_id else None


def _value_func(data: dict, apply_func, key: str = 'value'):
    values = data.get(key, data.get('value', []))
    return list(map(apply_func, values))


def copy_measurement(term_id: str, data: dict):
    measurement = _new_measurement(term_id, MODEL)
    return _omit(data, ['description', 'method']) | measurement


def slice_by_year(term_id: str, dates: list, values: list):
    def group_values(group: dict, index: int):
        try:
            date = dates[index]
            value = values[index]
            month = dates[index][0:4]
            group[month] = group.get(month, []) + [(date, value)]
        except IndexError:
            pass
        return group

    def iterate_values(data: list):
        return (
            measurement_value({
                'term': {
                    '@id': term_id,
                    'termType': TermTermType.MEASUREMENT.value
                },
                'value': non_empty_list([v for (_d, v) in data])
            }, is_larger_unit=True),
            data[0][0],
            data[-1][0]
        ) if has_all_months([d for (d, _v) in data]) else None

    values_by_month = reduce(group_values, range(0, len(dates)), {})
    return non_empty_list(map(iterate_values, values_by_month.values()))


def _extract_year_month(date: str):
    try:
        year = int(date[0:4])
        month = int(date[5:7])
        return year, month
    except Exception:
        return None, None


def group_by_month(term_id: str, dates: list, values: list):
    def group_values(group: dict, index: int):
        date = dates[index]
        value = values[index]
        month = dates[index][0:7]
        group[month] = group.get(month, []) + [(date, value)]
        return group

    def map_to_month(data: list, year: int, month: int):
        # make sure we got all the necessary days
        difference = last_day_of_month(year, month) - first_day_of_month(year, month)
        days_in_month = round(difference.days + difference.seconds / DAY, 1) + 1

        return measurement_value({
            'term': {
                '@id': term_id,
                'termType': TermTermType.MEASUREMENT.value
            },
            'value': non_empty_list([v for (_d, v) in data])
        }, is_larger_unit=True) if len(data) == days_in_month else None

    values_by_month = reduce(group_values, range(0, len(dates)), {}) if len(dates) == len(values) else {}

    values = []
    dates = []
    for month, data in values_by_month.items():
        year, m = _extract_year_month(data[0][0])
        # date might not contain a year or a month, cannot handle it
        value = map_to_month(data, year, m) if year and m else None
        if value is not None:
            dates.append(month)
            values.append(value)

    return values, dates
