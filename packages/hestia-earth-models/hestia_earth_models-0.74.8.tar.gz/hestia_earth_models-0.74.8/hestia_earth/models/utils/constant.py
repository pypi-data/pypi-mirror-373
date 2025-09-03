from enum import Enum

from hestia_earth.utils.tools import list_sum

DAYS_IN_YEAR = 365.25
DAYS_PER_MONTH = DAYS_IN_YEAR/12


class Units(Enum):
    BOOLEAN = 'boolean'
    HEAD = 'head'
    NUMBER = 'number'
    KG = 'kg'
    KG_DRY_MATTER = 'kg dry matter'
    KG_CA = 'kg Ca'
    KG_CACO3 = 'kg CaCO3'
    KG_CAO = 'kg CaO'
    KG_CH4 = 'kg CH4'
    KG_CO2 = 'kg CO2'
    KG_K = 'kg K'
    KG_K2O = 'kg K2O'
    KG_CAMGCO32 = 'kg CaMg(CO3)2'
    KG_N = 'kg N'
    KG_N2 = 'kg N2'
    KG_N2O = 'kg N2O'
    KG_NH3 = 'kg NH3'
    KG_NH4 = 'kg NH4'
    KG_NO2 = 'kg NO2'
    KG_NO3 = 'kg NO3'
    KG_NOX = 'kg NOx'
    KG_P = 'kg P'
    KG_P2O5 = 'kg P2O5'
    KG_PO43 = 'kg PO43'
    KG_VS = 'kg VS'
    KG_LIVEWEIGHT = 'kg liveweight'
    KG_COLD_CARCASS_WEIGHT = 'kg cold carcass weight'
    KG_COLD_DRESSED_CARCASS_WEIGHT = 'kg cold dressed carcass weight'
    KG_READY_TO_COOK_WEIGHT = 'kg ready-to-cook weight'
    PERCENTAGE_AREA = '% area'
    TO_C = '-C'
    TO_N = '-N'
    KW_H = 'kWh'
    MJ = 'MJ'
    M3 = "m3"


C = 12.012
CA = 40.078
H = 1.008
K = 39.098
MG = 24.305
N = 14.007
_O = 15.999
P = 30.974
ATOMIC_WEIGHT_CONVERSIONS = {
    Units.KG_P.value: {
        Units.KG_P2O5.value: (P*2) / (P*2 + _O*5),
        Units.KG_PO43.value: P / ((P + _O*4)*3)
    },
    Units.KG_PO43.value: {
        Units.KG_P2O5.value: ((P + _O*4)*3) / (P*2 + _O*5)
    },
    Units.KG_P2O5.value: {
        Units.KG_P.value: (P*2 + _O*5) / (P*2)
    },
    Units.KG_K.value: {
        Units.KG_K2O.value: (K*2) / (K*2 + _O)
    },
    Units.KG_CA.value: {
        Units.KG_CAO.value: CA / (CA + _O)
    },
    Units.KG_CAO.value: {
        Units.KG_CACO3.value: (CA + _O) / (CA + C + _O*3)
    },
    Units.KG_CACO3.value: {
        Units.KG_CO2.value: (CA + C + _O*3) / C
    },
    Units.KG_CAMGCO32.value: {
        Units.KG_CO2.value: (CA + MG + (C + _O*3)*2) / (C*2)
    },
    Units.KG_CH4.value: {
        Units.TO_C.value: (C + H*4) / C
    },
    Units.KG_CO2.value: {
        Units.TO_C.value: (C + _O*2) / C
    },
    Units.KG_NOX.value: {
        Units.TO_N.value: (N + _O) / N
    },
    Units.KG_N2.value: {
        Units.TO_N.value: 1
    },
    Units.KG_N2O.value: {
        Units.TO_N.value: (N*2 + _O) / (N*2)
    },
    Units.KG_NO2.value: {
        Units.TO_N.value: (N + _O*2) / N
    },
    Units.KG_NO3.value: {
        Units.TO_N.value: (N + _O*3) / N
    },
    Units.KG_NH3.value: {
        Units.TO_N.value: (N + H*3) / N
    },
    Units.KG_NH4.value: {
        Units.TO_N.value: (N + H*4) / N
    },
    Units.KW_H.value: {
        Units.MJ.value: 3.6
    },
}


def get_atomic_conversion(src_unit: Units, dest_unit: Units, default_value=1):
    src_key = src_unit if isinstance(src_unit, str) else src_unit.value
    dest_key = dest_unit if isinstance(dest_unit, str) else dest_unit.value
    return ATOMIC_WEIGHT_CONVERSIONS.get(src_key, {}).get(dest_key, default_value)


def convert_to_unit(node: dict, dest_unit: Units, default_value=None):
    value = list_sum(node.get('value', []), default=None)
    conversion = get_atomic_conversion(node.get('term', {}).get('units'), dest_unit, default_value=None)
    return value / conversion if all([value is not None, conversion is not None]) else default_value


def convert_to_N(node: dict):
    conversion = get_atomic_conversion(node.get('term', {}).get('units'), Units.TO_N, 0)
    return list_sum(node.get('value', [])) / conversion if conversion != 0 else 0
