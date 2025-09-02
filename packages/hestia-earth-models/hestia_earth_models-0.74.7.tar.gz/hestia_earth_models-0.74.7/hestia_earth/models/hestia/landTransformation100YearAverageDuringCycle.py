from .resourceUse_utils import run_resource_use

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "management": [{"@type": "Management", "value": ">=0", "term.termType": "landCover", "endDate": ""}]
        },
        "emissionsResourceUse": [
            {
                "@type": "Indicator",
                "term.@id": "landOccupationDuringCycle",
                "landCover": {
                    "@type": "Term",
                    "termType": "landCover"
                },
                "value": ">=0"
            }
        ],
        "endDate": "",
        "none": {
            "cycle": {
                "@type": "Cycle",
                "otherSites": []
            }
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "landCover": "",
        "previousLandCover": ""
    }]
}
LOOKUPS = {
    "crop": "IPCC_LAND_USE_CATEGORY"
}
TERM_ID = 'landTransformation100YearAverageDuringCycle'
_HISTORIC_DATE_OFFSET = 100


def run(impact_assessment: dict):
    return run_resource_use(
        impact_assessment=impact_assessment,
        historic_date_offset=_HISTORIC_DATE_OFFSET,
        term_id=TERM_ID
    )
