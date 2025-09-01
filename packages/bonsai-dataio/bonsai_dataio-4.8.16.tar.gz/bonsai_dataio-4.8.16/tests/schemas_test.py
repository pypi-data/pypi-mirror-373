import json
import math
from typing import Dict

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

import dataio.schemas.bonsai_api as schemas
from dataio.tools import BonsaiTableModel


def test_usage_of_attribute_names():
    assert schemas.Emissions_uncertainty.names.activity == "activity"
    assert schemas.CountryRecipe.names.act_code == "act_code"


# Define the pytest function
def test_to_dataclass_from_dataframe_Use():
    # Define the test data
    test_data = {
        "location": ["AT", "AT", "AT"],
        "product": ["C_AGSL", "C_ALUW", "C_AL_INCI"],
        "activity": ["A_REFN", "A_ALUW", "A_AL_INCI"],
        "unit": ["tonnes", "tonnes", "tonnes"],
        "value": [577.4442373, 385165.449, 168989.1224],
        "flag": ["1", "a", "1"],
        "time": [2016, 2016, 2016],
        "variance": [2, 3, 2.5],
        "product_origin": ["Origin1", "Origin2", "Origin3"],  # Adding product origins
    }
    # Convert the test data to a DataFrame
    test_df = pd.DataFrame(test_data)

    # Define the expected output
    expected_output = BonsaiTableModel(
        data=[
            schemas.Use_uncertainty(
                location="AT",
                product="C_AGSL",
                activity="A_REFN",
                unit="tonnes",
                value=577.4442373,
                flag="1",
                variance=2.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin1",
                product_type="use",
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_ALUW",
                activity="A_ALUW",
                unit="tonnes",
                value=385165.449,
                flag="a",
                variance=3.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin2",
                product_type="use",
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_AL_INCI",
                activity="A_AL_INCI",
                unit="tonnes",
                value=168989.1224,
                flag="1",
                variance=2.5,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin3",
                product_type="use",
            ),
        ],
    )

    # Call the function with the test DataFrame and data class
    result = schemas.Use_uncertainty.to_dataclass(test_df)
    print(result)
    # Assert that the result matches the expected output
    assert result == expected_output


def test_to_dataclass_from_dataframe_Use_no_uncertainty():
    # Define the test data
    test_data = {
        "location": ["AT", "AT", "AT"],
        "product": ["C_AGSL", "C_ALUW", "C_AL_INCI"],
        "activity": ["A_REFN", "A_ALUW", "A_AL_INCI"],
        "unit": ["tonnes", "tonnes", "tonnes"],
        "value": [577.4442373, 385165.449, 168989.1224],
        "flag": ["1", "1", "1"],
        "time": [2016, 2016, 2016],
        "product_origin": ["Origin1", "Origin2", "Origin3"],  # Adding product origins
    }
    # Convert the test data to a DataFrame
    test_df = pd.DataFrame(test_data)

    # Define the expected output
    expected_output = BonsaiTableModel(
        data=[
            schemas.Use_uncertainty(
                location="AT",
                product="C_AGSL",
                activity="A_REFN",
                unit="tonnes",
                value=577.4442373,
                flag="1",
                time=2016,
                product_origin="Origin1",
                product_type="use",
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_ALUW",
                activity="A_ALUW",
                unit="tonnes",
                value=385165.449,
                flag="1",
                time=2016,
                product_origin="Origin2",
                product_type="use",
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_AL_INCI",
                activity="A_AL_INCI",
                unit="tonnes",
                value=168989.1224,
                flag="1",
                time=2016,
                product_origin="Origin3",
                product_type="use",
            ),
        ],
    )

    # Call the function with the test DataFrame and data class
    result = schemas.Use_uncertainty.to_dataclass(test_df)

    # Assert that the result matches the expected output
    assert result == expected_output


def test_to_dataclass_from_dataframe_USE_with_optional():
    # Define the test data
    test_data = {
        "location": ["AT", "AT", "AT"],
        "product": ["C_AGSL", "C_ALUW", "C_AL_INCI"],
        "activity": ["A_REFN", "A_ALUW", "A_AL_INCI"],
        "unit": ["tonnes", "tonnes", "tonnes"],
        "value": [577.4442373, 385165.449, 168989.1224],
        "flag": ["1", "1", "1"],
        "time": [2016, 2016, 2016],
        "variance": [2, 3, 2.5],
        "standard_deviation": [None, 2, None],
        "product_origin": ["Origin1", "Origin2", "Origin3"],  # Adding product origins
    }
    # Convert the test data to a DataFrame
    test_df = pd.DataFrame(test_data)

    # Define the expected output
    expected_output = BonsaiTableModel(
        data=[
            schemas.Use_uncertainty(
                location="AT",
                product="C_AGSL",
                activity="A_REFN",
                unit="tonnes",
                value=577.4442373,
                flag="1",
                variance=2.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin1",
                product_type="use",
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_ALUW",
                activity="A_ALUW",
                unit="tonnes",
                value=385165.449,
                flag="1",
                variance=3.0,
                standard_deviation=2.0,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin2",
                product_type="use",
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_AL_INCI",
                activity="A_AL_INCI",
                unit="tonnes",
                value=168989.1224,
                flag="1",
                variance=2.5,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin3",
                product_type="use",
            ),
        ],
    )

    # Call the function with the test DataFrame and data class
    result = schemas.Use_uncertainty.to_dataclass(test_df)

    # Assert that the result matches the expected output
    assert len(result.data) == len(expected_output.data)
    for res, exp in zip(result.data, expected_output.data):
        assert res.location == exp.location
        assert res.product == exp.product
        assert res.activity == exp.activity
        assert res.unit == exp.unit
        assert res.value == exp.value
        assert res.flag == exp.flag
        assert res.time == exp.time


def test_to_dataclass_from_dataframe_wasteuse():
    # Sample data
    test_data = {
        "location": ["AT", "AT", "AT"],
        "product": ["C_AGSL", "C_ALUW", "C_AL_INCI"],
        "activity": ["A_REFN", "A_ALUW", "A_AL_INCI"],
        "unit": ["tonnes", "tonnes", "tonnes"],
        "value": [577.4442373, 385165.449, 168989.1224],
        "flag": ["1", "1", "1"],
        "time": [2016, 2016, 2016],
        "variance": [2, 3, 2.5],
        "product_origin": ["Origin1", "Origin2", "Origin3"],  # Adding product origins
        "waste_fraction": [True, False, True],
    }
    # Convert the test data to a DataFrame
    test_df = pd.DataFrame(test_data)

    # Define the expected output
    expected_output = BonsaiTableModel(
        data=[
            schemas.WasteUse_uncertainty(
                location="AT",
                product="C_AGSL",
                activity="A_REFN",
                unit="tonnes",
                value=577.4442373,
                flag="1",
                variance=2.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin1",
                product_type="waste_use",
                waste_fraction=True,
            ),
            schemas.WasteUse_uncertainty(
                location="AT",
                product="C_ALUW",
                activity="A_ALUW",
                unit="tonnes",
                value=385165.449,
                flag="1",
                variance=3.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin2",
                product_type="waste_use",
                waste_fraction=False,
            ),
            schemas.WasteUse_uncertainty(
                location="AT",
                product="C_AL_INCI",
                activity="A_AL_INCI",
                unit="tonnes",
                value=168989.1224,
                flag="1",
                variance=2.5,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin3",
                product_type="waste_use",
                waste_fraction=True,
            ),
        ],
    )

    # Call the function with the test DataFrame and data class
    result = schemas.WasteUse_uncertainty.to_dataclass(test_df)

    # Assert that the result matches the expected output
    assert result == expected_output


def test_get_empty_dataframe_Use():
    result = schemas.Use_uncertainty.get_empty_dataframe()
    assert result.empty

    expected_columns = [
        "variance",
        "standard_deviation",
        "confidence_interval_95min",
        "confidence_interval_95max",
        "confidence_interval_68min",
        "confidence_interval_68max",
        "distribution",
        "min_value",
        "max_value",
        "uncertainty_comment",
        "location",
        "product",
        "activity",
        "unit",
        "value",
        "associated_product",
        "flag",
        "time",
        "product_origin",
        "product_type",
        "account_type",
    ]
    assert list(result.columns) == expected_columns


def test_data_class_to_json():
    data = BonsaiTableModel(
        data=[
            schemas.Recipe(
                prefixed_id="AM_1234567890",
                flow="Flow1",
                region_reference="Region1",
                unit_reference="Unit1",
                flow_input="Input1",
                region_inflow=None,
                value_inflow=None,
                unit_inflow=None,
                value_emission=10.5,
                unit_emission="kg",
                metrics="Metric1",
                variance=2.5,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
            ),
            schemas.Recipe(
                prefixed_id="AF_2345678901",
                flow="Flow2",
                region_reference="Region2",
                unit_reference="Unit2",
                flow_input="Input2",
                region_inflow="AT",
                value_inflow=25,
                unit_inflow="Unit4",
                value_emission=20.3,
                unit_emission="g",
                metrics="Metric2",
                variance=None,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
            ),
            schemas.Recipe(
                prefixed_id="AM_3456789012",
                flow="Flow3",
                region_reference="Region3",
                unit_reference="Unit3",
                flow_input="Input3",
                region_inflow=None,
                value_inflow=None,
                unit_inflow=None,
                value_emission=15.2,
                unit_emission="mg",
                metrics="Metric3",
                variance=1,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
            ),
        ]
    )
    result = data.to_json()

    expected_result = {
        "data": [
            {
                "variance": 2.5,
                "standard_deviation": None,
                "confidence_interval_95min": None,
                "confidence_interval_95max": None,
                "confidence_interval_68min": None,
                "confidence_interval_68max": None,
                "distribution": None,
                "min_value": None,
                "max_value": None,
                "uncertainty_comment": None,
                "prefixed_id": "AM_1234567890",
                "flow": "Flow1",
                "region_reference": "Region1",
                "unit_reference": "Unit1",
                "flow_input": "Input1",
                "region_inflow": None,
                "value_inflow": None,
                "unit_inflow": None,
                "value_emission": 10.5,
                "unit_emission": "kg",
                "metrics": "Metric1",
            },
            {
                "variance": None,
                "standard_deviation": None,
                "confidence_interval_95min": None,
                "confidence_interval_95max": None,
                "confidence_interval_68min": None,
                "confidence_interval_68max": None,
                "distribution": None,
                "min_value": None,
                "max_value": None,
                "uncertainty_comment": None,
                "prefixed_id": "AF_2345678901",
                "flow": "Flow2",
                "region_reference": "Region2",
                "unit_reference": "Unit2",
                "flow_input": "Input2",
                "region_inflow": "AT",
                "value_inflow": 25.0,
                "unit_inflow": "Unit4",
                "value_emission": 20.3,
                "unit_emission": "g",
                "metrics": "Metric2",
            },
            {
                "variance": 1.0,
                "standard_deviation": None,
                "confidence_interval_95min": None,
                "confidence_interval_95max": None,
                "confidence_interval_68min": None,
                "confidence_interval_68max": None,
                "distribution": None,
                "min_value": None,
                "max_value": None,
                "uncertainty_comment": None,
                "prefixed_id": "AM_3456789012",
                "flow": "Flow3",
                "region_reference": "Region3",
                "unit_reference": "Unit3",
                "flow_input": "Input3",
                "region_inflow": None,
                "value_inflow": None,
                "unit_inflow": None,
                "value_emission": 15.2,
                "unit_emission": "mg",
                "metrics": "Metric3",
            },
        ]
    }
    expected_json_result = json.dumps(expected_result, indent=4)

    assert result == expected_json_result


def test_to_dataclass_from_json_Supply():
    expected_result = BonsaiTableModel(
        data=[
            schemas.Supply_uncertainty(
                location="Region1",
                product="Flow1",
                activity="Input1",
                unit="Unit1",
                value=3.0,
                flag="1",
                variance=2.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=1998,
                product_type="supply",
            ),
            schemas.Supply_uncertainty(
                location="Region2",
                product="Flow2",
                activity="Input2",
                unit="Unit2",
                value=25.0,
                flag="2",
                variance=3.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=1998,
                product_type="supply",
            ),
            schemas.Supply_uncertainty(
                location="Region3",
                product="Flow3",
                activity="Input3",
                unit="Unit3",
                value=23.0,
                flag="3",
                variance=2.5,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=1998,
                product_type="supply",
            ),
        ],
    )

    jsondata = {
        "data": [
            {
                "location": "Region1",
                "product": "Flow1",
                "activity": "Input1",
                "unit": "Unit1",
                "value": 3,
                "flag": "1",
                "variance": 2,
                "time": 1998,
            },
            {
                "location": "Region2",
                "product": "Flow2",
                "activity": "Input2",
                "unit": "Unit2",
                "value": 25.0,
                "flag": "2",
                "variance": 3,
                "time": 1998,
            },
            {
                "location": "Region3",
                "product": "Flow3",
                "activity": "Input3",
                "unit": "Unit3",
                "value": 23,
                "flag": "3",
                "variance": 2.5,
                "time": 1998,
            },
        ],
    }
    result = schemas.Supply_uncertainty.to_dataclass(jsondata)

    assert result == expected_result


def test_to_dataclass_from_json_Supply_no_uncertainty():
    expected_result = BonsaiTableModel(
        data=[
            schemas.Supply_uncertainty(
                location="Region1",
                product="Flow1",
                activity="Input1",
                unit="Unit1",
                value=3.0,
                flag="1",
                time=1998,
                product_type="supply",
            ),
            schemas.Supply_uncertainty(
                location="Region2",
                product="Flow2",
                activity="Input2",
                unit="Unit2",
                value=25.0,
                flag="2",
                time=1998,
                product_type="supply",
            ),
            schemas.Supply_uncertainty(
                location="Region3",
                product="Flow3",
                activity="Input3",
                unit="Unit3",
                value=23.0,
                flag="3",
                time=1998,
                product_type="supply",
            ),
        ],
    )

    jsondata = {
        "data": [
            {
                "location": "Region1",
                "product": "Flow1",
                "activity": "Input1",
                "unit": "Unit1",
                "value": 3,
                "flag": "1",
                "time": 1998,
            },
            {
                "location": "Region2",
                "product": "Flow2",
                "activity": "Input2",
                "unit": "Unit2",
                "value": 25.0,
                "flag": "2",
                "time": 1998,
            },
            {
                "location": "Region3",
                "product": "Flow3",
                "activity": "Input3",
                "unit": "Unit3",
                "value": 23,
                "flag": "3",
                "time": 1998,
            },
        ],
    }
    result = schemas.Supply_uncertainty.to_dataclass(jsondata)

    assert result == expected_result


def test_to_dataclass_from_json_WasteSupply():
    expected_result = BonsaiTableModel(
        data=[
            schemas.Supply_uncertainty(
                location="Region1",
                product="Flow1",
                activity="Input1",
                unit="Unit1",
                value=3.0,
                flag="1",
                variance=2.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=1998,
                product_type="supply",
                waste_fraction=True,
            ),
            schemas.Supply_uncertainty(
                location="Region2",
                product="Flow2",
                activity="Input2",
                unit="Unit2",
                value=25.0,
                flag="2",
                variance=3.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=1998,
                product_type="supply",
                waste_fraction=False,
            ),
            schemas.Supply_uncertainty(
                location="Region3",
                product="Flow3",
                activity="Input3",
                unit="Unit3",
                value=23.0,
                flag="3",
                variance=2.5,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=1998,
                product_type="supply",
                waste_fraction=True,
            ),
        ],
    )

    jsondata = {
        "data": [
            {
                "location": "Region1",
                "product": "Flow1",
                "activity": "Input1",
                "unit": "Unit1",
                "value": 3,
                "flag": "1",
                "variance": 2,
                "time": 1998,
                "waste_fraction": True,
            },
            {
                "location": "Region2",
                "product": "Flow2",
                "activity": "Input2",
                "unit": "Unit2",
                "value": 25.0,
                "flag": "2",
                "variance": 3,
                "time": 1998,
                "waste_fraction": False,
            },
            {
                "location": "Region3",
                "product": "Flow3",
                "activity": "Input3",
                "unit": "Unit3",
                "value": 23,
                "flag": "3",
                "variance": 2.5,
                "time": 1998,
                "waste_fraction": True,
            },
        ],
    }
    result = schemas.Supply_uncertainty.to_dataclass(jsondata)

    assert result == expected_result


def test_to_pandas_Use():
    test_data = BonsaiTableModel(
        data=[
            schemas.Use_uncertainty(
                location="AT",
                product="C_AGSL",
                activity="A_REFN",
                unit="tonnes",
                value=577.4442373,
                associated_product=None,
                flag="1",
                variance=2.0,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin1",
                product_type="use",
                account_type=None,
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_ALUW",
                activity="A_ALUW",
                unit="tonnes",
                value=385165.449,
                associated_product=None,
                flag="1",
                variance=3.0,
                standard_deviation=2.0,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin2",
                product_type="use",
                account_type=None,
            ),
            schemas.Use_uncertainty(
                location="AT",
                product="C_AL_INCI",
                activity="A_AL_INCI",
                unit="tonnes",
                value=168989.1224,
                associated_product=None,
                flag="1",
                variance=2.5,
                standard_deviation=None,
                confidence_interval_95min=None,
                confidence_interval_95max=None,
                confidence_interval_68min=None,
                confidence_interval_68max=None,
                distribution=None,
                mean_default=None,
                uncertainty_comment=None,
                max_value=None,
                min_value=None,
                time=2016,
                product_origin="Origin3",
                product_type="use",
                account_type=None,
            ),
        ],
    )

    result = test_data.to_pandas()

    test_dataframe = {
        "location": ["AT", "AT", "AT"],
        "product": ["C_AGSL", "C_ALUW", "C_AL_INCI"],
        "activity": ["A_REFN", "A_ALUW", "A_AL_INCI"],
        "unit": ["tonnes", "tonnes", "tonnes"],
        "value": [577.4442373, 385165.449, 168989.1224],
        "associated_product": [None, None, None],
        "flag": ["1", "1", "1"],
        "variance": [2.0, 3.0, 2.5],
        "standard_deviation": [None, 2.0, None],
        "confidence_interval_95min": [None, None, None],
        "confidence_interval_95max": [None, None, None],
        "confidence_interval_68min": [None, None, None],
        "confidence_interval_68max": [None, None, None],
        "distribution": [None, None, None],
        "uncertainty_comment": [None, None, None],
        "max_value": [None, None, None],
        "min_value": [None, None, None],
        "time": [2016, 2016, 2016],
        "product_origin": ["Origin1", "Origin2", "Origin3"],
        "product_type": ["use", "use", "use"],
        "account_type": [None, None, None],
    }
    expected_output = pd.DataFrame(test_dataframe)

    # Ensure columns are in the same order for comparison
    result = result.reindex(sorted(result.columns), axis=1)
    expected_output = expected_output.reindex(sorted(expected_output.columns), axis=1)

    pd.testing.assert_frame_equal(result, expected_output)
    assert_frame_equal(result, expected_output)


def test_to_pandas_Use():
    test_data = BonsaiTableModel(
        data=[
            schemas.Use_samples(
                location="AT",
                product="C_AGSL",
                activity="A_REFN",
                unit="tonnes",
                value=577.4442373,
                associated_product=None,
                flag="1",
                time=2016,
                product_origin="Origin1",
                product_type="use",
                samples=[1, 2, 3],
                account_type=None,
            ),
            schemas.Use_samples(
                location="AT",
                product="C_ALUW",
                activity="A_ALUW",
                unit="tonnes",
                value=385165.449,
                associated_product=None,
                flag="1",
                time=2016,
                product_origin="Origin2",
                product_type="use",
                samples=[1, 2],
                account_type=None,
            ),
            schemas.Use_samples(
                location="AT",
                product="C_AL_INCI",
                activity="A_AL_INCI",
                unit="tonnes",
                value=168989.1224,
                associated_product=None,
                flag="1",
                time=2016,
                product_origin="Origin3",
                product_type="use",
                samples=[3, 2, 1],
                account_type=None,
            ),
        ],
    )

    result = test_data.to_pandas()

    test_dataframe = {
        "location": ["AT", "AT", "AT"],
        "product": ["C_AGSL", "C_ALUW", "C_AL_INCI"],
        "activity": ["A_REFN", "A_ALUW", "A_AL_INCI"],
        "unit": ["tonnes", "tonnes", "tonnes"],
        "value": [577.4442373, 385165.449, 168989.1224],
        "associated_product": [None, None, None],
        "flag": ["1", "1", "1"],
        "time": [2016, 2016, 2016],
        "product_origin": ["Origin1", "Origin2", "Origin3"],
        "product_type": ["use", "use", "use"],
        "samples": [[1, 2, 3], [1, 2], [3, 2, 1]],
        "account_type": [None, None, None],
    }
    expected_output = pd.DataFrame(test_dataframe)

    # Ensure columns are in the same order for comparison
    result = result.reindex(sorted(result.columns), axis=1)
    expected_output = expected_output.reindex(sorted(expected_output.columns), axis=1)

    pd.testing.assert_frame_equal(result, expected_output)
    assert_frame_equal(result, expected_output)


def test_get_dtypes():
    fields = schemas.Supply_uncertainty.get_csv_field_dtypes()
    expected_fields = {
        "location": "str",
        "product": "str",
        "activity": "str",
        "associated_product": "str",
        "unit": "str",
        "value": "float",
        "flag": "str",
        "time": "int",
        "product_type": "str",
        "product_destination": "str",
        "variance": "float",
        "standard_deviation": "float",
        "confidence_interval_95min": "float",
        "confidence_interval_95max": "float",
        "confidence_interval_68min": "float",
        "confidence_interval_68max": "float",
        "distribution": "str",
        "min_value": "float",
        "max_value": "float",
        "uncertainty_comment": "str",
        "account_type": "str",
    }
    assert expected_fields == fields


def test_transform_dataframe():
    data_schema = schemas.PRODCOMProductionVolume.get_empty_dataframe()
    data_schema_transformed = schemas.ProductionVolumes_uncertainty.transform_dataframe(
        data_schema
    )
    expected_result = schemas.ProductionVolumes_uncertainty.get_empty_dataframe()

    # Sort columns to ensure order doesn't affect the comparison
    data_schema_transformed = data_schema_transformed.sort_index(axis=1)
    expected_result = expected_result.sort_index(axis=1)

    # Ensure no differences in columns
    assert data_schema_transformed.columns.equals(
        expected_result.columns
    ), "Column names do not match"

    # Check for equality
    pd.testing.assert_frame_equal(
        data_schema_transformed,
        expected_result,
        check_dtype=True,
        check_index_type="equiv",
        check_like=True,
    )


def test_get_classification():
    # Directly call the class method without instantiating
    result = schemas.PRODCOMProductionVolume.get_classification()

    # Define expected classification dictionary
    expected_classification = {
        "location": ("geonumeric", "location"),
        "product": (
            "prodcom_total_2_0",
            "flowobject",
        ),  # could also be prodcom_sold_2_0 depending on context
    }

    # Assert that the result from the method matches the expected dictionary
    assert (
        result == expected_classification
    ), f"Expected {expected_classification} but got {result}"
