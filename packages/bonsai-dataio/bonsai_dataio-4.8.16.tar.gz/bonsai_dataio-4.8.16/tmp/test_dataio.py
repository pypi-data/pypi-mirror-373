import datetime
import logging
import os
from decimal import Decimal
from pathlib import Path

import data_io.data_io as io
import pandas as pd
import pytest
import yaml
from data_io.dataclasses import (
    Algorithm,
    AttributeTable,
    Author,
    DataPackage,
    FactTable,
    Field,
    IncompleteDatapackageException,
    License,
    ModifiedBy,
    Source,
)

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def test_file_dir():
    return Path("tests") / "data"


def test_read_basic_data_package_from_disk(test_file_dir):
    """
    This test reads a valid frictionless datapackage to a DataPackage object from the
    current version.
    """

    config = {"name": "datacube", "path": test_file_dir / "test_data_cube"}

    data_package = io.read(config)

    climate_zone_attr_frame = AttributeTable(
        pd.DataFrame(
            [
                ["region with mainly boreal and temperate climate", 0],
                ["region with mainly tropical climate", 1],
            ],
            index=pd.Index(["boreal_temperate", "tropical"], name="code"),
            columns=["description", "position"],
        ),
        {
            "code": Field(name="code"),
            "description": Field(name="description"),
            "position": Field(name="position"),
        },
        "ISO3",
        "misc",
    )
    country_attr_frame = AttributeTable(
        pd.DataFrame(
            [["Algeria", 0], ["Angola", 1], ["Anguilla", 2], ["Argentina", 4]],
            index=pd.Index(["Algeria", "Angola", "Anguilla", "Argentina"], name="code"),
            columns=["description", "position"],
        ),
        {
            "code": Field(name="code"),
            "description": Field(name="description"),
            "position": Field(name="position"),
        },
        "ISO3",
        "region",
    )
    property_attr_frame = AttributeTable(
        pd.DataFrame(
            [
                ["default", "mean", 0],
                ["minimum", "2.5th percentile", 1],
                ["maximum", "97.5th percentile", 2],
            ],
            index=pd.Index(["def", "min", "max"], name="code"),
            columns=["description", "remarks", "position"],
        ),
        {
            "code": Field(name="code"),
            "description": Field(name="description"),
            "remarks": Field(name="remarks"),
            "position": Field(name="position"),
        },
        "ISOSomething",
        "something",
    )
    swds_type_attr_frame = AttributeTable(
        pd.DataFrame(
            [
                ["Managed solid waste disposal site (anaerobic).", 0],
                ["Well managed solid waste disposal site (semi-aerobic).", 1],
                ["Poorly managed solid waste disposal site (semi-aerobic).", 2],
            ],
            index=pd.Index(
                ["managed", "managed_well_s-a", "managed_poorly_s-a"], name="code"
            ),
            columns=["description", "position"],
        ),
        {
            "code": Field(name="code"),
            "description": Field(name="description"),
            "position": Field(name="position"),
        },
        "Something",
        "something",
    )
    unit_attr_frame = AttributeTable(
        pd.DataFrame(
            [
                ["capita", 0],
                ["tonnes per capita per year", 1],
                ["kilogram per kilogram", 2],
                ["per year", 3],
                ["no unit", 4],
            ],
            index=pd.Index(["cap", "t/cap/yr", "kg/kg", "1/yr", "none"], name="code"),
            columns=["description", "position"],
        ),
        {
            "code": Field(name="code"),
            "description": Field(name="description"),
            "position": Field(name="position"),
        },
        "unit",
        "unit",
    )
    year_attr_frame = AttributeTable(
        pd.DataFrame(
            [["year in which activity occurs", 0]],
            index=pd.Index(["2010"], name="code"),
            columns=["description", "position"],
        ),
        {
            "code": Field(name="code"),
            "description": Field(name="description"),
            "position": Field(name="position"),
        },
        "year",
        "period",
    )

    climate_zone_frame = FactTable(
        pd.DataFrame(
            [
                "boreal_temperate",
                "tropical",
                "tropical",
                "boreal_temperate",
            ],
            index=pd.MultiIndex.from_arrays(
                [
                    ["a0", "a1", "a2", "a4"],
                    ["Albania", "Algeria", "Angola", "Argentina"],
                ],
                names=["id", "country"],
            ),
            columns=["value"],
        ),
        fields={
            "value": Field(name="value"),
            "id": Field(name="id", foreign_name="code", resource="climate_zone_dim"),
            "country": Field(name="id", foreign_name="code", resource="country"),
        },
    )
    mcf_frame = FactTable(
        pd.DataFrame(
            [
                1,
                0.9,
                1,
                0.3,
            ],
            index=pd.MultiIndex.from_arrays(
                [
                    ["a0", "a1", "a2", "a4"],
                    ["managed", "managed", "managed", "managed_well_s-a"],
                    ["def", "min", "max", "min"],
                    ["kg/kg", "kg/kg", "kg/kg", "kg/kg"],
                ],
                names=["id", "swds_type", "property", "unit"],
            ),
            columns=["value"],
        ),
        fields={
            "value": Field(name="value"),
            "id": Field(name="id", foreign_name="code", resource="mcf_dim"),
            "swds_type": Field(
                name="swds_type", foreign_name="code", resource="swds_type"
            ),
            "property": Field(
                name="property", foreign_name="code", resource="property_dim"
            ),
        },
    )
    urb_pop_frame = FactTable(
        pd.DataFrame(
            [
                24299170.0,
                13963065.0,
                37055902.0,
            ],
            index=pd.MultiIndex.from_arrays(
                [
                    ["a0", "a1", "a3"],
                    [2010, 2010, 2010],
                    ["Algeria", "Angola", "Argentina"],
                    ["def", "def", "def"],
                    ["cap", "cap", "cap"],
                ],
                names=["id", "year", "country", "property", "unit"],
            ),
            columns=["value"],
        ),
        fields={
            "value": Field(name="value"),
            "id": Field(name="id", foreign_name="code", resource="mcf_dim"),
            "country": Field(name="country", foreign_name="code", resource="country"),
            "property": Field(
                name="property", foreign_name="code", resource="property_dim"
            ),
            "year": Field(name="year", foreign_name="code", resource="year"),
            "unit": Field(name="unit", foreign_name="code", resource="unit"),
        },
    )

    tables = {
        "par_climate_zone": climate_zone_frame,
        "par_mcf": mcf_frame,
        "par_urb_population": urb_pop_frame,
        "dim_climate_zone": climate_zone_attr_frame,
        "country": country_attr_frame,
        "dim_property": property_attr_frame,
        "dim_swds_type": swds_type_attr_frame,
        "unit": unit_attr_frame,
        "year": year_attr_frame,
    }

    exptected_license = License(
        "MIT",
        "MIT License",
        "this is actually not a data license",
        "https://www.mitlicense.com",
    )
    exptected_source = Source(
        reference="Something",
        encoding="utf-8",
        link="https://www.example.com",
        link_doc="http://www.example.com/docs",
        authors=["Joe", "Paul", "Melinda", "Anna"],
        institution="Harvard",
        type="SUT",
        license=exptected_license,
        language="en",
    )
    exptected_author = Author(
        "Valentin Starlinger", "2.-0 LCA Consultants", "valentin.starlinger@lca-net.com"
    )
    exptected_algorithm = Algorithm(name="clean/faostat", version_number=0)
    exptected_modified_by = ModifiedBy(
        authors=[exptected_author], algorithm=exptected_algorithm
    )
    expected_package = DataPackage(
        name="datacube",
        category_path="this/is/something",
        version="1.2.3",
        title="Example of a composite data cube stored in tabular format",
        comment="Based on the IPCC waste data collected by Maik Budzinski",
        tables=tables,
        source=exptected_source,
        modified_by=exptected_modified_by,
        last_modified=datetime.datetime(
            2023, 2, 23, 13, 20, 51, tzinfo=datetime.timezone.utc
        ),
        target_language="en",
        encoding="utf-8",
    )

    assert expected_package.name == data_package.name
    assert expected_package.category_path == data_package.category_path
    assert expected_package.title == data_package.title
    assert expected_package.comment == data_package.comment
    assert expected_package.source == data_package.source
    assert expected_package.modified_by == data_package.modified_by
    assert expected_package.last_modified == data_package.last_modified
    assert expected_package.target_language == data_package.target_language
    assert expected_package.encoding == data_package.encoding

    assert tables.keys() == data_package.tables.keys()

    for name, table in tables.items():
        print(name)
        pd.testing.assert_frame_equal(table.data, data_package.tables[name].data)


@pytest.fixture
def sample_datapackage():
    # Create sample data for testing
    fact_data = pd.DataFrame(
        {"region": [1, 2], "industry": [2, 3], "value": [0.1, 2.3]}
    )
    fact_data = fact_data.set_index(["region", "industry"])
    attr_data = pd.DataFrame({"code": [1, 2], "name": ["Region 1", "Region 2"]})
    attr_data = attr_data.set_index(["code"])
    # Create sample DataPackage instance
    license = License(
        "CC BY 4.0",
        "Creative Commons Attribution 4.0",
        "",
        "https://creativecommons.org/licenses/by/4.0/",
    )
    source = Source(
        "Sample Source", "UTF-8", "", ["John Doe"], "Acme Inc.", "CSV", license, "en"
    )
    author = Author("John Doe", "Acme Inc.", "john.doe@acme.com")
    algorithm = Algorithm("Sample Algorithm", "1.0")
    modified_by = ModifiedBy([author], algorithm)
    tables = {
        "fact_table": FactTable(
            fact_data,
            {
                "region": Field("region", "code", "region"),
                "industry": Field("industry"),
                "value": Field("value"),
            },
        ),
        "region": AttributeTable(
            attr_data,
            {"code": Field("code"), "name": Field("name")},
            "region_name",
            "region",
        ),
    }

    datapackage = DataPackage(
        "sample_data",
        "example/path",
        "1.0.0",
        title="Sample Data",
        comment="Sample data for testing",
        tables=tables,
        source=source,
        modified_by=modified_by,
        last_modified=datetime.datetime(
            2023, 2, 23, 13, 20, 51, tzinfo=datetime.timezone.utc
        ),
        target_language="en",
        encoding="UTF-8",
    )

    return datapackage


def test_write_read(sample_datapackage, tmp_path):
    param_dict = {"root_path": tmp_path}
    io.write(param_dict, sample_datapackage)

    # Test if the required files are created
    data_path = tmp_path / "example" / "path" / "sample_data" / "1" / "0" / "0"
    assert (data_path / "fact_table.csv").exists()
    assert (data_path / "region.csv").exists()
    assert (data_path / "sample_data.datapackage.yaml").exists()

    # print("fact table")
    # with open(data_path / "fact_table.csv", "r") as file:
    #    for line in file.readlines():
    #        print(line, end="")
    # print("attr table")
    # with open(data_path / "region.csv", "r") as file:
    #    for line in file.readlines():
    #        print(line, end="")
    # print("metadata")
    # with open(data_path / "sample_data.datapackage.yaml", "r") as file:
    #    for line in file.readlines():
    #        print(line, end="")

    # Read DataPackage
    param_dict = {"name": "sample_data", "path": data_path}
    read_datapackage = io.read(param_dict)

    print(sample_datapackage)
    print()
    print()
    print(read_datapackage)

    # Compare the original and read DataPackages
    assert sample_datapackage == read_datapackage


def test_incomplete_datapackage_exception(sample_datapackage, tmp_path):
    param_dict = {"root_path": tmp_path}

    # Test missing name
    sample_datapackage.name = None
    with pytest.raises(
        IncompleteDatapackageException, match="DataPackage name field missing"
    ):
        io.write(param_dict, sample_datapackage)
    sample_datapackage.name = "sample_data"

    # Test missing source
    sample_datapackage.source = None
    with pytest.raises(
        IncompleteDatapackageException, match="DataPackage source field missing"
    ):
        io.write(param_dict, sample_datapackage)
    sample_datapackage.source = Source(
        "Sample Source",
        "UTF-8",
        "",
        ["John Doe"],
        "Acme Inc.",
        "CSV",
        sample_datapackage.license,
        "en",
    )

    # Test missing modified_by
    sample_datapackage.modified_by = None
    with pytest.raises(
        IncompleteDatapackageException, match="DataPackage modified_by field missing"
    ):
        io.write(param_dict, sample_datapackage)
    sample_datapackage.modified_by = ModifiedBy(
        [Author("John Doe", "Acme Inc.", "john.doe@acme.com")],
        Algorithm("Sample Algorithm", "1.0"),
    )

    # Test missing target_language
    sample_datapackage.target_language = None
    with pytest.raises(
        IncompleteDatapackageException,
        match="DataPackage target_language field missing",
    ):
        io.write(param_dict, sample_datapackage)
    sample_datapackage.target_language = "en"


def test_version_to_path():
    assert io._version_to_path("1.0.0") == Path("1/0/0")
    assert io._version_to_path("2.1a.3") == Path("2/1a/3")
    assert io._version_to_path("2.3") == Path("2/3")

    with pytest.raises(ValueError):
        io._version_to_path("1")  # Invalid version string

    with pytest.raises(ValueError):
        io._version_to_path("1.a.0.3")  # Invalid version string


def test_category_path_to_path():
    assert io._category_path_to_path("A/B/C") == Path("A/B/C")
    assert io._category_path_to_path("X/Y/Z") == Path("X/Y/Z")

    with pytest.raises(ValueError):
        io._category_path_to_path("A//B/C")  # Invalid category_path string

    with pytest.raises(ValueError):
        io._category_path_to_path("A/B\\C")  # Invalid category_path string

    with pytest.raises(ValueError):
        io._category_path_to_path("A\B\C")  # Invalid category_path string


def test_incomplete_datapackage_exception():
    datapackage = DataPackage("", "", "")

    with pytest.raises(
        IncompleteDatapackageException, match="DataPackage name field missing"
    ):
        io.write({"root_path": "root"}, datapackage)

    datapackage.name = "test"
    with pytest.raises(
        IncompleteDatapackageException, match="DataPackage source field missing"
    ):
        io.write({"root_path": "root"}, datapackage)
