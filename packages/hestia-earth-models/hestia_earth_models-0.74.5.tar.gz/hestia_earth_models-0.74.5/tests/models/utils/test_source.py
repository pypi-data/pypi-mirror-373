from unittest.mock import patch

from hestia_earth.models.utils.source import _list_sources, find_sources

class_path = 'hestia_earth.models.utils.source'
search_results = [{
    '@type': 'Source',
    '@id': 'source-1',
    'name': 'Source 1',
    'bibliography': {'title': 'Biblio 1'}
}]


def test_list_sources():
    sources = _list_sources()
    assert sorted(sources) == [
        '2006 IPCC Guidelines for National Greenhouse Gas Inventories',
        '2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories',
        'A critical review of the conventional SOC to SOM conversion factor',
        'An Enhanced Global Elevation Model Generalized From Multiple Higher Resolution Source Datasets',
        'Biofuels: a new methodology to estimate GHG emissions from global land use change',
        'COMMISSION DECISION of 10 June 2010 on guidelines for the calculation of land carbon stocks for the purpose of Annex V to Directive 2009/28/EC',  # noqa: E501
        'Contribution of Organic Matter and Clay to Soil Cation-Exchange Capacity as Affected by the pH of the Saturating Solution',  # noqa: E501
        'ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate',
        'Harmonized World Soil Database Version 1.2. Food and Agriculture Organization of the United Nations (FAO).',  # noqa: E501
        'Harmonized World Soil Database Version 2.0.',
        'Modelling spatially explicit impacts from phosphorus emissions in agriculture',
        'Reducing food’s environmental impacts through producers and consumers',
        'Soil organic carbon sequestration rates in vineyard agroecosystems under different soil management practices: A meta-analysis',  # noqa: E501
    ]


@patch(f"{class_path}.search", return_value=search_results)
def test_find_sources(*args):
    sources = find_sources()
    assert sources == {
        'Biblio 1': {
            '@type': 'Source',
            '@id': 'source-1',
            'name': 'Source 1'
        }
    }
