from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.utils.cycle import cycle_end_year
from hestia_earth.models.utils.lookup import get_region_lookup_value

EMBER_ECOINVENT_LOOKUP_NAME = "ember-ecoinvent-mapping.csv"
REGION_EMBER_SOURCES_LOOKUP_NAME = "region-ember-energySources.csv"


def get_input_coefficient(model: str, cycle: dict, country_id: str, ecoinventName: str):
    year = cycle_end_year(cycle)

    # find the matching ember source with the ecoinventName.
    # example: "electricity, high voltage, electricity production, hard coal" > "Coal"
    ember_ecoinvent_lookup = download_lookup(EMBER_ECOINVENT_LOOKUP_NAME)
    source_name = get_table_value(ember_ecoinvent_lookup, column_name('ecoinventName'), ecoinventName, 'ember')

    # find the ratio for the country / year
    data = get_region_lookup_value(REGION_EMBER_SOURCES_LOOKUP_NAME, country_id, source_name, model=model)
    percentage = extract_grouped_data(data, str(year))
    return safe_parse_float(percentage, default=0) / 100
