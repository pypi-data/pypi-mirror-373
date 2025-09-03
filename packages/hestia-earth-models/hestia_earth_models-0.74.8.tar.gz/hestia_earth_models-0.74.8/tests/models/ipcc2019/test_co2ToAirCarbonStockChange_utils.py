from hestia_earth.schema import EmissionMethodTier, MeasurementMethodClassification

from hestia_earth.models.ipcc2019.co2ToAirCarbonStockChange_utils import (
    _add_carbon_stock_change_emissions, _calc_carbon_stock_change, _calc_carbon_stock_change_emission,
    _convert_c_to_co2, _lerp_carbon_stocks, CarbonStock, CarbonStockChange, CarbonStockChangeEmission
)


def test_convert_c_to_co2():
    KG_C = 1000
    EXPECTED = 3663.836163836164
    assert _convert_c_to_co2(KG_C) == EXPECTED


def test_lerp_carbon_stocks():
    START = CarbonStock(20000, "2000-12-31", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    END = CarbonStock(22000, "2002-12-31", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    TARGET_DATE = "2001-12-31"
    EXPECTED = CarbonStock(
        21000, "2001-12-31", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT
    )

    result = _lerp_carbon_stocks(START, END, TARGET_DATE)
    assert result == EXPECTED


def test_calc_carbon_stock_change():
    START = CarbonStock(20000, "2000", MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    END = CarbonStock(21000,  "2001", MeasurementMethodClassification.TIER_1_MODEL)
    EXPECTED = CarbonStockChange(1000, "2000", "2001", MeasurementMethodClassification.TIER_1_MODEL)

    result = _calc_carbon_stock_change(START, END)
    assert result == EXPECTED


def test_calc_carbon_stock_change_emission():
    SOC_STOCK_CHANGE = CarbonStockChange(-1000, "2000", "2001", MeasurementMethodClassification.TIER_1_MODEL)
    EXPECTED = CarbonStockChangeEmission(3663.836163836164, "2000", "2001", EmissionMethodTier.TIER_1)

    result = _calc_carbon_stock_change_emission(SOC_STOCK_CHANGE)
    assert result == EXPECTED


def test_add_carbon_stock_change_emissions():
    EMISSION_1 = CarbonStockChangeEmission(3000, "2000", "2001", EmissionMethodTier.TIER_1)
    EMISSION_2 = CarbonStockChangeEmission(2000, "2001", "2002", EmissionMethodTier.TIER_1)
    EXPECTED = CarbonStockChangeEmission(5000, "2000", "2002", EmissionMethodTier.TIER_1)

    result = _add_carbon_stock_change_emissions(EMISSION_1, EMISSION_2)
    assert result == EXPECTED
