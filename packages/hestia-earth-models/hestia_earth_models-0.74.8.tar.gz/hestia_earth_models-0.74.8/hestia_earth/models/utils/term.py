from typing import Union
from functools import lru_cache
import json
from hestia_earth.schema import SchemaType, TermTermType, SiteSiteType
from hestia_earth.utils.storage import _load_from_storage
from hestia_earth.utils.api import find_node, search, download_hestia
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

from .constant import Units
from ..log import debugMissingLookup

# avoid running scroll
LIMIT = 9999


def get_lookup_value(lookup_term: dict, column: str, skip_debug: bool = False, **log_args):
    table_name = f"{lookup_term.get('termType')}.csv" if lookup_term else None
    value = get_table_value(
        download_lookup(table_name), 'termid', lookup_term.get('@id'), column_name(column)
    ) if table_name else None
    debugMissingLookup(
        table_name, 'termid', lookup_term.get('@id'), column, value, **log_args
    ) if lookup_term and not skip_debug else None
    return value


@lru_cache()
def _load_term_file(term_type: str):
    try:
        filepath = f"glossary/{term_type}.json"
        nodes = json.loads(_load_from_storage(filepath, glossary=True))
        return {node.get('@id'): node for node in nodes}
    except Exception as e:
        print(e)
        return {}


def download_term(term: Union[str, dict], termType: Union[str, TermTermType] = None):
    term_id = term.get('@id', term.get('id')) if isinstance(term, dict) else term
    term_type = (
        termType if isinstance(termType, str) else termType.value
    ) if termType else (
        term.get('termType') if isinstance(term, dict) else None
    )
    cached_nodes = _load_term_file(term_type) if term_type else {}
    return cached_nodes.get(term_id) or download_hestia(term_id)


def get_liquid_fuel_terms():
    """
    Find all "liquid" `fuel` terms from the Glossary:
    - https://hestia.earth/glossary?termType=fuel&query=gasoline
    - https://hestia.earth/glossary?termType=fuel&query=petrol
    - https://hestia.earth/glossary?termType=fuel&query=diesel

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.FUEL.value
                    }
                }
            ],
            "should": [
                {
                    "regexp": {
                        "name": "gasoline*"
                    }
                },
                {
                    "regexp": {
                        "name": "petrol*"
                    }
                },
                {
                    "regexp": {
                        "name": "diesel*"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_wood_fuel_terms():
    """
    Find all "wood" `fuel` terms from the Glossary that have a `Energy content (lower heating value)` property:
    - https://hestia.earth/glossary?termType=fuel&query=wood

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.FUEL.value
                    }
                },
                {
                    "nested": {
                        "path": "defaultProperties",
                        "query": {
                            "match": {
                                "defaultProperties.term.name.keyword": "Energy content (lower heating value)"
                            }
                        }
                    }
                },
                {
                    "regexp": {
                        "name": "wood*"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_irrigation_terms():
    """
    Find all `water` terms from the Glossary:
    https://hestia.earth/glossary?termType=water

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.WATER.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_urea_terms():
    """
    Find all `inorganicFertiliser` urea terms from the Glossary:
    https://hestia.earth/glossary?termType=inorganicFertiliser&query=urea

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.INORGANICFERTILISER.value,
        'name': 'urea'
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_excreta_N_terms():
    """
    Find all `excreta` terms in `kg N` from the Glossary:
    https://hestia.earth/glossary?termType=excreta

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.EXCRETA.value,
        'units.keyword': Units.KG_N.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_excreta_VS_terms():
    """
    Find all `excreta` terms in `kg Vs` from the Glossary:
    https://hestia.earth/glossary?termType=excreta

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.EXCRETA.value,
        'units.keyword': Units.KG_VS.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_tillage_terms():
    """
    Find all `landUseManagement` terms of "tillage" from the Glossary:
    https://hestia.earth/glossary?termType=tillage&query=tillage

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.TILLAGE.value,
        'name': 'tillage'
    }, limit=LIMIT)
    return [n['@id'] for n in terms if 'depth' not in n['@id'].lower()]


def get_generic_crop():
    """
    Find `Generic crop seed` from the Glossary:
    https://hestia.earth/glossary?termType=crop&query=Generic%20crop%20seed

    Returns
    -------
    str
        Matching term `@id`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.CROP.value,
        'name': 'Generic crop seed'
    }, limit=1)
    return terms[0] if len(terms) > 0 else None


def get_rice_paddy_terms():
    """
    Find all `crop` terms of "rice paddy" from the Glossary:
    https://hestia.earth/glossary?termType=crop&query=rice%20paddy

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType": TermTermType.CROP.value
                    }
                },
                {
                    "regexp": {
                        "name": "rice*"
                    }
                },
                {
                    "regexp": {
                        "name": "flooded*"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return [n['@id'] for n in terms if 'depth' not in n['@id'].lower()]


def get_flooded_pre_season_terms():
    """
    Find all `landUseManagement` terms of "flooded pre season" from the Glossary:
    https://hestia.earth/glossary?termType=landUseManagement&query=flooded%20pre-season

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType": TermTermType.LANDUSEMANAGEMENT.value
                    }
                },
                {
                    "match_phrase": {
                        "name": "flooded pre-season"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_crop_residue_terms():
    """
    Find all `cropResidue` terms from the Glossary:
    https://hestia.earth/glossary?termType=cropResidue

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {'termType.keyword': TermTermType.CROPRESIDUE.value}, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_digestible_energy_terms():
    """
    Find all "digestible energy" `property` terms from the Glossary:
    https://hestia.earth/glossary?termType=property&query=digestible%20energy

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.PROPERTY.value
                    }
                },
                {
                    "match_phrase_prefix": {
                        "name": "Digestible energy"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_energy_digestibility_terms():
    """
    Find all "energy digestibility" `property` terms from the Glossary:
    https://hestia.earth/glossary?termType=property&query=energy%digestibility

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.PROPERTY.value
                    }
                },
                {
                    "match_phrase_prefix": {
                        "name": "Energy digestibility"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_crop_residue_management_terms():
    """
    Find all `cropResidueManagement` terms from the Glossary:
    https://hestia.earth/glossary?termType=cropResidueManagement

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {'termType.keyword': TermTermType.CROPRESIDUEMANAGEMENT.value}, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_all_emission_terms():
    """
    Find all `emission` terms from the Glossary:
    https://hestia.earth/glossary?termType=emission

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {"termType.keyword": TermTermType.EMISSION.value}, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_milkYield_terms():
    """
    Find all "milk yield" `animalManagement` terms from the Glossary:
    https://hestia.earth/glossary?query=milk%20yield&termType=animalManagement

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.ANIMALMANAGEMENT.value
                    }
                },
                {
                    "match_phrase_prefix": {
                        "name": "Milk yield"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_wool_terms():
    """
    Find all "wool" `animalProduct` terms from the Glossary:
    https://hestia.earth/glossary?query=wool&termType=animalProduct

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.ANIMALPRODUCT.value
                    }
                },
                {
                    "match_phrase_prefix": {
                        "name": "Wool"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_cover_crop_property_terms():
    """
    Find all property terms related to cover crops from the Glossary:
    - https://www.hestia.earth/glossary?query=cover%20crop&termType=property
    - https://www.hestia.earth/glossary?query=catch%20crop&termType=property
    - https://www.hestia.earth/glossary?query=fallow%20crop&termType=property

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.PROPERTY.value}}
            ],
            "should": [
                {"match_phrase": {"name": "cover crop"}},
                {"match_phrase": {"name": "catch crop"}},
                {"match_phrase": {"name": "fallow crop"}},
                {"match_phrase": {"synonyms": "cover crop"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_crop_residue_incorporated_or_left_on_field_terms():
    """
    Find all `cropResidue` terms for residues incorporated or left on field.
    - https://www.hestia.earth/glossary?query=incorporated&termType=cropResidue
    - https://www.hestia.earth/glossary?query=left%20on%20field&termType=cropResidue
    - https://www.hestia.earth/glossary?query=below%20ground&termType=cropResidue

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type.keyword": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.CROPRESIDUE.value}}
            ],
            "should": [
                {"match": {"name": "incorporated"}},
                {"match_phrase": {"name": "left on field"}},
                {"match_phrase": {"name": "below ground"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_irrigated_terms():
    """
    Find all `waterRegime` management/practice terms with names containing "irrigated" and "deep water"
    from the Glossary:
    - https://hestia.earth/glossary?termType=waterRegime&query=irrigated
    - https://hestia.earth/glossary?termType=waterRegime&query=deep%20water

    n.b., this function differs from `get_irrigation_terms` which returns all `water` input terms.

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.WATERREGIME.value}}
            ],
            "should": [
                {"match_phrase_prefix": {"name": "irrigated"}},
                {"match_phrase_prefix": {"name": "deep water"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_residue_removed_or_burnt_terms():
    """
    Find all `cropResidueManagement` terms where residues are removed or burnt from the Glossary

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.CROPRESIDUEMANAGEMENT.value}}
            ],
            "should": [
                {"match": {"name": "removed"}},
                {"match": {"name": "burnt"}}
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_upland_rice_land_cover_terms():
    """
    Find all `landCover` terms related to upland rice the Glossary.

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.LANDCOVER.value}},
                {"match_phrase": {"name": "rice plant"}},
                {"match": {"name": "upland"}}
            ],
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_upland_rice_crop_terms():
    """
    Find all `crop` terms related to upland rice the Glossary.

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.CROP.value}},
                {"match_phrase": {"name": "rice"}},
                {"match": {"name": "upland"}}
            ],
        }
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_pasture_system_terms():
    """
    Find all `system` terms with the name `pasture`:
    https://hestia.earth/glossary?termType=system&query=pasture

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.SYSTEM.value,
        'name': 'pasture'
    }, limit=LIMIT)
    return list(map(lambda n: n["@id"], terms))


def get_electricity_grid_mix_terms():
    """
    Find all `Electricity` terms with the name `grid mix`:
    https://hestia.earth/glossary?termType=electricity&query=grid%20mix

    Returns
    -------
    list
        List of matching `Term` as dict.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType.keyword": TermTermType.ELECTRICITY.value}},
                {"match": {"name": "grid"}},
                {"match": {"name": "mix"}}
            ],
        }
    }, limit=LIMIT, fields=['@type', '@id', 'name', 'termType', 'units'])
    return list(map(lambda n: n["@id"], terms))


def get_land_cover_siteTypes():
    """
    Find all `Land Cover` terms with siteTypes

    Returns
    -------
        List of landCover terms with associated siteTypes.
    """
    return search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType": TermTermType.LANDCOVER.value}}
            ],
            "should": [{"match": {"name": siteType.value}} for siteType in SiteSiteType],
            "minimum_should_match": 1
        },
    }, limit=LIMIT)


def get_land_cover_terms():
    """
    Find all `Land Cover` terms from the Glossary: https://hestia.earth/glossary?termType=landCover

    Returns
    -------
        List of landCover terms IDs.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match": {"termType": TermTermType.LANDCOVER.value}}
            ]
        },
    }, limit=LIMIT, fields=['@id'])
    return list(map(lambda n: n["@id"], terms))


def get_ionophore_terms():
    """
    Find all `Ionophore` terms from the Glossary: https://hestia.earth/glossary?query=ionophore

    Returns
    -------
        List of ionophore term IDs.
    """
    terms = search({
        "bool": {
            "must": [
                {"match": {"@type": SchemaType.TERM.value}},
                {"match_phrase_prefix": {"name": "ionophore"}}
            ],
            "should": [
                {"match": {"termType": TermTermType.FEEDFOODADDITIVE.value}},
                {"match": {"termType": TermTermType.VETERINARYDRUG.value}},

            ],
            "minimum_should_match": 1
        },
    }, limit=LIMIT, fields=['@id'])
    return list(map(lambda n: n["@id"], terms))
