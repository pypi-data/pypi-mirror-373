from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import extract_grouped_data
from hestia_earth.utils.tools import non_empty_list, safe_parse_float, safe_parse_date

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.term import download_term
from hestia_earth.models.utils.currency import DEFAULT_CURRENCY
from hestia_earth.models.utils.crop import FAOSTAT_PRODUCTION_LOOKUP_COLUMN, get_crop_grouping_faostat_production
from hestia_earth.models.utils.animalProduct import FAO_LOOKUP_COLUMN, get_animalProduct_grouping_fao
from hestia_earth.models.utils.product import convert_product_to_unit
from hestia_earth.models.utils.lookup import get_region_lookup_value
from ..utils import get_liveAnimal_to_animalProduct_id
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "term.termType": ["crop", "animalProduct", "liveAnimal"]
        }],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        }
    }
}
RETURNS = {
    "Product": [{
        "price": ""
    }]
}
LOOKUPS = {
    "@doc": "Depending on the primary product [termType](https://hestia.earth/schema/Product#term)",
    "crop": "cropGroupingFaostatProduction",
    "region-crop-cropGroupingFaostatProduction-price": "",
    "liveAnimal": ["primaryMeatProductFaoPriceTermId"],
    "animalProduct": ["animalProductGroupingFAOEquivalent", "animalProductGroupingFAO"],
    "region-animalProduct-animalProductGroupingFAO-price": "",
    "region-animalProduct-animalProductGroupingFAO-averageColdCarcassWeight": "",
    "region-animalProduct-animalProductGroupingFAO-weightPerItem": ""
}
MODEL_KEY = 'price'
LOOKUP_NAME = {
    TermTermType.CROP.value: f"region-{TermTermType.CROP.value}-{FAOSTAT_PRODUCTION_LOOKUP_COLUMN}-price.csv",
    TermTermType.ANIMALPRODUCT.value: f"region-{TermTermType.ANIMALPRODUCT.value}-{FAO_LOOKUP_COLUMN}-price.csv"
}
LOOKUP_GROUPING = {
    TermTermType.CROP.value: get_crop_grouping_faostat_production,
    TermTermType.ANIMALPRODUCT.value: get_animalProduct_grouping_fao
}
LOOKUP_UNITS_NUMBER = {
    TermTermType.ANIMALPRODUCT.value: f"region-{TermTermType.ANIMALPRODUCT.value}-{FAO_LOOKUP_COLUMN}-weightPerItem.csv"
}


def _term_grouping(term: dict): return LOOKUP_GROUPING.get(term.get('termType'), lambda *_: None)(MODEL, term)


def _lookup_data(
    term_id: str, grouping: str, country: dict, year: int, term_type: str = None, lookup_name: str = None
):
    lookup_name = lookup_name or LOOKUP_NAME.get(term_type, '')

    def get_data(country_id):
        data = get_region_lookup_value(lookup_name, country_id, grouping, model=MODEL, term=term_id, key=MODEL_KEY)
        price = extract_grouped_data(data, str(year)) or extract_grouped_data(data, 'Average_price_per_tonne')
        return safe_parse_float(price, default=None)

    # try get country data first, falls back to region data
    country_id = country.get('@id')
    region_id = (country.get('subClassOf') or [{}])[0].get('@id')
    return get_data(country_id) or (get_data(region_id) if region_id else None)


def _product(product: dict, value: float):
    # currency in lookup table is set to USD
    return product | {'currency': DEFAULT_CURRENCY, MODEL_KEY: round(value, 4)}


def _get_liveAnimal_lookup_values(cycle: dict, product: dict, country: dict, year: int = None):
    term_id = product.get('term', {}).get('@id')
    animal_product = get_liveAnimal_to_animalProduct_id(term_id, LOOKUPS['liveAnimal'][0], key=MODEL_KEY)
    groupingFAO = _term_grouping({'termType': TermTermType.ANIMALPRODUCT.value, '@id': animal_product})

    # one live animal can be linked to many animal product, hence go one by one until we have a match
    if groupingFAO:
        price_per_ton_liveweight = _lookup_data(
            term_id, groupingFAO, country, year, term_type=TermTermType.ANIMALPRODUCT.value
        )
        debugValues(cycle, model=MODEL, term=term_id, key=MODEL_KEY, by='liveAnimal',
                    animal_product=animal_product,
                    price_per_ton_liveweight=price_per_ton_liveweight,
                    groupingFAO=f"'{groupingFAO}'")
        if price_per_ton_liveweight:
            # price is per 1000kg, divide by 1000 to go back to USD/kg
            return (animal_product, price_per_ton_liveweight / 1000)
    return (None, None)


def _run_by_liveAnimal(cycle: dict, product: dict, country: dict, year: int = None):
    term_id = product.get('term', {}).get('@id')
    animal_product_id, price_per_kg_liveweight = _get_liveAnimal_lookup_values(cycle, product, country, year)

    animal_product = download_term(animal_product_id, TermTermType.ANIMALPRODUCT)
    price_per_head = convert_product_to_unit({
        **product,
        'term': animal_product,
        'value': [price_per_kg_liveweight]
    }, Units.HEAD) if price_per_kg_liveweight else None

    logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY, by='liveAnimal',
                    year=year,
                    price_per_kg_liveweight=price_per_kg_liveweight,
                    price_per_head=price_per_head)

    should_run = all([animal_product, price_per_head])
    logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY, by='liveAnimal')

    return _product(product, price_per_head) if price_per_head is not None else None


def _should_run_liveAnimal(product: dict):
    return product.get('term', {}).get('termType') == TermTermType.LIVEANIMAL.value


def _run_by_country(cycle: dict, product: dict, country: dict, year: int = None):
    product_term = product.get('term', {})
    term_id = product_term.get('@id')
    term_type = product_term.get('termType')
    term_units = product_term.get('units')

    has_yield = len(product.get('value') or []) > 0
    not_already_set = MODEL_KEY not in product.keys()

    # get the grouping used in region lookup
    grouping = _term_grouping(product_term) or None

    should_run = all([not_already_set, has_yield, grouping])
    value = _lookup_data(term_id, grouping, country, year, term_type=term_type) if should_run else None

    # if units is number instead of kg, need to convert to number first
    conversion_to_number = safe_parse_float(
        get_region_lookup_value(LOOKUP_UNITS_NUMBER.get(term_type), country.get('@id'), grouping), default=1
    ) if term_units == Units.NUMBER.value else 1

    logRequirements(cycle, model=MODEL, term=term_id, key=MODEL_KEY, by='country',
                    has_yield=has_yield,
                    not_already_set=not_already_set,
                    year=year,
                    price_per_ton=value,
                    groupingFAO=f"'{grouping}'",
                    conversion_to_number=conversion_to_number)

    logShouldRun(cycle, MODEL, term_id, should_run, key=MODEL_KEY, by='country')

    # divide by 1000 to convert price per tonne to kg
    return _product(product, value / 1000 * conversion_to_number) if value is not None else None


def _should_run_product(product: dict): return product.get(MODEL_KEY) is None


def run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    end_date = safe_parse_date(cycle.get('endDate'))
    year = end_date.year if end_date else None

    products = list(filter(_should_run_product, cycle.get('products', [])))
    return non_empty_list([
        (
            (
                (_run_by_liveAnimal(cycle, p, country, year) if _should_run_liveAnimal(p) else None)
                or _run_by_country(cycle, p, country, year)
            ) if country else None
        ) for p in products
    ])
