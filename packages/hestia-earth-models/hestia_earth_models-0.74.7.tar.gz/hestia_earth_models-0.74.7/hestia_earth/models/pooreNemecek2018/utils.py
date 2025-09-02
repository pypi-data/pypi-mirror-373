from functools import reduce
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match, filter_list_term_type, find_primary_product
from hestia_earth.utils.tools import non_empty_list, list_average, list_sum
from hestia_earth.utils.lookup import extract_grouped_data

from hestia_earth.models.log import logShouldRun, logRequirements, log_as_table
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL


def run_products_average(cycle: dict, term_id: str, get_value_func):
    products = cycle.get('products', [])

    values_by_product = [
        (p.get('term', {}).get('@id'), get_value_func(p)) for p in products
    ]
    values = non_empty_list([
        value for term_id, value in values_by_product
    ])
    has_values = len(values) > 0

    logRequirements(cycle, model=MODEL, term=term_id,
                    has_values=has_values,
                    details=log_as_table([
                        {'id': term_id, 'value': value} for term_id, value in values_by_product
                    ]))

    should_run = all([has_values])
    logShouldRun(cycle, MODEL, term_id, should_run)
    return list_average(values) if should_run else None


def _excreta_product_id(data: str, term_id):
    value = extract_grouped_data(data, term_id) or ''
    return value.split('|')[0] if '|' in value else value


def get_excreta_product_with_ratio(cycle: dict, lookup: str, **log_args):
    product = find_primary_product(cycle) or {}

    data = get_lookup_value(product.get('term'), lookup, model=MODEL, **log_args)

    # TODO: handle multiple products delimited by `|`
    default_product_id = _excreta_product_id(data, 'default')

    # find matching practices and assign a ratio for each
    # if no matches, use default id with 100% ratio
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.SYSTEM)
    practices = [
        {
            'id': practice.get('term', {}).get('@id'),
            'product-id': _excreta_product_id(data, practice.get('term', {}).get('@id')) or default_product_id,
            'value': list_sum(practice.get('value'))
        }
        for practice in practices
        # only keep practices with positive value
        if list_sum(practice.get('value', [-1]), 0) > 0
    ]
    logRequirements(cycle, model=MODEL, **log_args,
                    practices=log_as_table(practices),
                    default_product_id=default_product_id)

    total_value = list_sum([p.get('value') for p in practices])

    # group practices by product id
    grouped_practices = reduce(lambda p, c: p | {
        c['product-id']: p.get(c['product-id'], []) + [c]
    }, practices, {})
    # calculate ratio for each product
    grouped_practices = [
        values[0] | {'ratio': round(list_sum([v.get('value') for v in values]) * 100 / total_value, 2)}
        for values in grouped_practices.values()
    ]

    practices_with_products = [
        (find_term_match(cycle.get('products', []), p.get('product-id')), p)
        for p in grouped_practices
    ]
    products = [
        (
            product or {
                '@type': 'Product',
                'term': {'@type': 'Term', '@id': practice.get('product-id')}
            }
        ) | {'value': [practice.get('ratio')]}
        for product, practice in practices_with_products
        # ignore matching products with an existing value
        if all([
            not product or not product.get('value', []),
            product or practice.get('product-id')
        ])
    ] if practices_with_products else None

    return products or non_empty_list([{
        '@type': 'Product',
        'term': {'@type': 'Term', '@id': default_product_id},
        'value': [100]
    } if default_product_id else None])
