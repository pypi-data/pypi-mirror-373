import os
import re
import tempfile
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PureWindowsPath

import numpy as np
import pandas as pd
import pytest

import dataio.schemas.bonsai_api as schemas
from dataio.config import Config
from dataio.resources import CSVResourceRepository, ResourceRepository


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["BONSAI_HOME"] = str(Path("tests").absolute())
    os.environ["DATAIO_ROOT"] = str(Path("tests").absolute())


@pytest.fixture
def setup_empty_csv_repository(tmp_path):
    # Setup a temporary directory with a test CSV file
    test_db_path = tmp_path / "test_resources"
    test_db_path.mkdir()

    assert test_db_path.absolute()

    repo = ResourceRepository(db_path=str(test_db_path), storage_method="local")
    return repo


@pytest.fixture
def test_resources():
    return ResourceRepository(db_path="data", storage_method="local")


def test_automatic_location():

    # test with set location
    expected_location = str(
        Path("tests").absolute() / "clean" / "task1" / "1.0" / "data.csv"
    )
    resource1 = schemas.DataResource(
        name="data",
        task_name="task1",
        stage="clean",
        location="{stage}/{task_name}/{version}/{resource_name}.csv",
        schema_name=schemas.Footprint,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )
    assert expected_location == resource1.location

    # test without set location
    resource2 = schemas.DataResource(
        name="data",
        task_name="task1",
        stage="clean",
        schema_name=schemas.Footprint,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
    )
    assert expected_location == resource2.location


def test_path_with_backslash_correctly_read_and_written():
    # test with set location
    expected_location = str(
        Path("tests").absolute() / "clean" / "task1" / "1.0" / "data.csv"
    )

    input_location = str(PureWindowsPath(expected_location))

    resource1 = schemas.DataResource(
        name="data",
        task_name="task1",
        stage="clean",
        location=input_location,
        schema_name=schemas.Footprint,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )
    assert expected_location == resource1.location


def test_get_latest_version_non_semantic(setup_empty_csv_repository):
    repo = setup_empty_csv_repository
    old_version = schemas.DataResource(
        name="test_resource",
        schema_name="TestSchema",
        location="path/to/resource_v1",
        task_name="test_task",
        stage="test_stage",
        data_flow_direction="input",
        data_version="2012b1",
        code_version="1.0.0",
        comment="test comment v1",
        last_update=datetime.now(),
        created_by="tester",
        license="MIT",
        license_url="http://example.com/license",
        dag_run_id="test_dag_run_id_v1",
    )
    new_version = schemas.DataResource(
        name="test_resource",
        schema_name="TestSchema",
        location="path/to/resource_v2",
        task_name="test_task",
        stage="test_stage",
        data_flow_direction="input",
        data_version="2014b3",
        code_version="1.0.0",
        comment="test comment v2",
        last_update=datetime.now(),
        created_by="tester",
        license="MIT",
        license_url="http://example.com/license",
        dag_run_id="test_dag_run_id_v2",
    )
    # Add sample resources to the repository
    repo.add_to_resource_list(old_version)
    repo.add_to_resource_list(new_version)

    # Get the latest version of the resource
    latest_resource = repo.get_latest_version(
        name="test_resource", task_name="test_task"
    )

    # Check that the latest version is returned
    assert latest_resource.data_version == "2014b3"


def test_get_latest_version(setup_empty_csv_repository):
    repo = setup_empty_csv_repository
    old_version = schemas.DataResource(
        name="test_resource",
        schema_name="TestSchema",
        location="path/to/resource_v1",
        task_name="test_task",
        stage="test_stage",
        data_flow_direction="input",
        data_version="1.0.0",
        code_version="1.0.0",
        comment="test comment v1",
        last_update=datetime.now(),
        created_by="tester",
        license="MIT",
        license_url="http://example.com/license",
        dag_run_id="test_dag_run_id_v1",
    )
    new_version = schemas.DataResource(
        name="test_resource",
        schema_name="TestSchema",
        location="path/to/resource_v2",
        task_name="test_task",
        stage="test_stage",
        data_flow_direction="input",
        data_version="2.0.0",
        code_version="1.0.0",
        comment="test comment v2",
        last_update=datetime.now(),
        created_by="tester",
        license="MIT",
        license_url="http://example.com/license",
        dag_run_id="test_dag_run_id_v2",
    )
    # Add sample resources to the repository
    repo.add_to_resource_list(old_version)
    repo.add_to_resource_list(new_version)

    # Get the latest version of the resource
    latest_resource = repo.get_latest_version(
        name="test_resource", task_name="test_task"
    )

    # Check that the latest version is returned
    assert latest_resource.data_version == "2.0.0"


def test_overwrite_and_update_resource(setup_empty_csv_repository):
    # write data should update a field if overwrite=True
    repo = setup_empty_csv_repository

    df = pd.DataFrame()
    repo.write_dataframe_for_task(
        data=df,
        name="resource_name",
        location="test/file.csv",
        data_version="1.2",
        comment="No comment",
        schema_name="Supply_uncertainty",
    )

    assert repo.get_resource_info(name="resource_name").comment == "No comment"

    with pytest.raises(FileExistsError):
        repo.write_dataframe_for_task(
            data=df,
            name="resource_name",
            data_version="1.2",
            comment="No new comment",
            license="CC BY 4.0",
            overwrite=False,
        )
    assert repo.get_resource_info(name="resource_name").comment == "No comment"

    repo.write_dataframe_for_task(
        data=df,
        name="resource_name",
        data_version="1.2",
        comment="I actually do have a comment",
        license="CC BY 4.0",
        overwrite=True,
    )

    assert len(repo.available_resources) == 1
    assert (
        repo.get_resource_info(name="resource_name").comment
        == "I actually do have a comment"
    )


def test_append(setup_empty_csv_repository):
    config = Config(current_task_name="test")
    repo = setup_empty_csv_repository
    name = "new_resource"

    output_test_file = Path(__file__).parent / "data" / "baci" / f"{name}.csv"
    if output_test_file.is_file():
        output_test_file.unlink()

    metadata = config.schemas.DataResource(
        name=f"data/{name}.csv",
        schema_name="Footprint",
        task_name="Footprint",
        stage="clean",
        location=f"data/baci/{name}.csv",
        data_version="1.1",
        code_version="1.1",
        license="license",
        comment="Dataset includes BACI trade data",
        created_by="__author__",
    )

    init_data = pd.DataFrame(
        {
            "flow_code": ["FC100"],
            "description": ["Emission from transportation"],
            "unit_reference": ["per vehicle"],
            "region_code": ["US"],
            "value": [123],
            "unit_emission": ["tonnes CO2eq"],
        }
    )

    repo.write_dataframe_for_resource(
        data=init_data, resource=metadata, overwrite=False, append=False
    )  # create a new file
    data_to_add = pd.DataFrame(
        {
            "flow_code": ["BC200"],
            "description": ["Emission"],
            "unit_reference": ["per bike"],
            "region_code": ["FR"],
            "value": [999],
            "unit_emission": ["tonnes CO2eq"],
        }
    )
    repo.write_dataframe_for_resource(
        data=data_to_add, resource=metadata, overwrite=False, append=True
    )

    output_test_file = Path(__file__).parent / "data" / "baci" / f"{name}.csv"
    retrieved_data = pd.read_csv(output_test_file)
    if output_test_file.is_file():
        output_test_file.unlink()

    assert (retrieved_data.columns == init_data.columns).all()

    if output_test_file.is_file():
        output_test_file.unlink()

    # Compare the original DataFrame with the retrieved one
    pd.testing.assert_frame_equal(
        pd.concat([init_data, data_to_add]).reset_index(drop=True),
        retrieved_data.reset_index(drop=True),
        check_dtype=False,
    )
    return None


def test_overwrite(setup_empty_csv_repository):
    config = Config(current_task_name="test")
    repo = setup_empty_csv_repository
    # remove file if exists
    name = "new_resource"
    output_test_file = Path(__file__).parent / "data" / "baci" / f"{name}.csv"
    if output_test_file.is_file():
        output_test_file.unlink()

    metadata = config.schemas.DataResource(
        name=f"data/{name}.csv",
        schema_name="Footprint",
        task_name="Footprint",
        stage="clean",
        location=f"data/baci/{name}.csv",
        data_version="1.1",
        code_version="1.1",
        license="license",
        comment="Dataset includes BACI trade data",
        created_by="__author__",
    )

    init_data = pd.DataFrame(
        {
            "flow_code": ["FC100"],
            "description": ["Emission from transportation"],
            "unit_reference": ["per vehicle"],
            "region_code": ["US"],
            "value": [123],
            "unit_emission": ["tonnes CO2eq"],
        }
    )
    repo.write_dataframe_for_resource(
        data=init_data, resource=metadata, overwrite=False, append=False
    )  # create a new file
    new_data = pd.DataFrame(
        {
            "flow_code": ["BC200"],
            "description": ["Emission"],
            "unit_reference": ["per bike"],
            "region_code": ["FR"],
            "value": [999],
            "unit_emission": ["tonnes CO2eq"],
        }
    )
    repo.write_dataframe_for_resource(
        data=new_data, resource=metadata, overwrite=True, append=False
    )

    retrieved_data = pd.read_csv(output_test_file)
    if output_test_file.is_file():
        output_test_file.unlink()

    assert (retrieved_data.columns == init_data.columns).all()

    # Compare the original DataFrame with the retrieved one
    pd.testing.assert_frame_equal(
        new_data.reset_index(drop=True),
        retrieved_data.reset_index(drop=True),
        check_dtype=False,
    )
    return None


def test_append_and_overwrite_equal_must_fail(setup_empty_csv_repository):
    # append==override
    repo = setup_empty_csv_repository

    df = pd.DataFrame()

    with pytest.raises(Exception):
        repo.write_dataframe_for_task(
            data=df,
            name="resource_name",
            location="test/file.csv",
            data_version="1.2",
            comment="No comment",
            schema_name="Supply_uncertainty",
            overwrite=True,
            append=True,
        )


def test_resource_exists(setup_empty_csv_repository):
    repo = setup_empty_csv_repository
    sample_resource = schemas.DataResource(
        name="test_exist",
        schema_name="TestSchema",
        location="path/to/resource",
        task_name="test_task",
        stage="test_stage",
        data_flow_direction="input",
        data_version="1.0.0",
        code_version="1.0.0",
        comment="test comment",
        last_update=date.today(),
        created_by="tester",
        dag_run_id="test_dag_run_id",
    )
    # Initially, the resource should not exist
    assert not repo.resource_exists(sample_resource)

    # Add the resource to the repository
    repo.add_to_resource_list(sample_resource)

    # Now, the resource should exist
    assert repo.resource_exists(sample_resource)


def test_add_to_resource_list(setup_empty_csv_repository):
    repo = setup_empty_csv_repository
    resource = schemas.DataResource(
        name="test_resource",
        schema_name="schema1",
        location=str(repo.db_path),
        task_name="task1",
        stage="raw",
        data_flow_direction="input",
        data_version="v1.0",
        code_version="c1.0",
        comment="Initial test comment",
        last_update=date.today(),
        created_by="tester",
        dag_run_id="12345",
    )
    repo.add_to_resource_list(resource)
    assert not repo.available_resources.empty
    assert repo.available_resources.iloc[-1]["name"] == "test_resource"


def test_update_resource_list(setup_empty_csv_repository):
    repo = setup_empty_csv_repository
    # Add a resource first
    resource = schemas.DataResource(
        name="test_resource",
        schema_name="schema1",
        location=str(repo.db_path),
        task_name="task1",
        stage="raw",
        data_flow_direction="input",
        data_version="v1.0",
        code_version="c1.0",
        comment="Initial test comment",
        last_update=date.today(),
        created_by="tester",
        dag_run_id="12345",
    )
    repo.add_to_resource_list(resource)
    # Update the same resource
    updated_comment = "Updated comment"
    resource.comment = updated_comment
    repo.update_resource_list(resource)
    assert (
        repo.available_resources.loc[
            repo.available_resources["name"] == "test_resource", "comment"
        ].iloc[0]
        == updated_comment
    )


def test_get_resource_info_with_filters(setup_empty_csv_repository):
    repo = setup_empty_csv_repository
    # Add some resources
    resource1 = schemas.DataResource(
        name="resource1",
        schema_name="schema1",
        location=str(repo.db_path),
        task_name="task1",
        stage="raw",
        data_flow_direction="input",
        data_version="v1.0",
        code_version="c1.0",
        comment="First resource",
        last_update=date.today(),
        created_by="tester",
        dag_run_id="12345",
    )
    resource2 = schemas.DataResource(
        name="resource2",
        schema_name="schema2",
        location=str(repo.db_path),
        task_name="task2",
        stage="processed",
        data_flow_direction="output",
        data_version="v2.0",
        code_version="c2.0",
        comment="Second resource",
        last_update=date.today(),
        created_by="tester",
        dag_run_id="12346",
    )
    repo.add_to_resource_list(resource1)
    repo.add_to_resource_list(resource2)
    # Test get with filters
    result = repo.get_resource_info(name="resource2")
    assert result.name == "resource2"


def test_list_available_resources(test_resources):
    repo = test_resources

    resources = repo.list_available_resources()
    assert isinstance(resources, list)
    assert len(resources) == 11

    # test if specific resource is loaded correctly
    result = repo.get_resource_info(name="SampleRegion", data_version="1.5")

    assert result.name == "SampleRegion"
    assert result.schema_name == "Location"
    assert result.location == str(
        Path("tests").absolute() / "data" / "SampleRegion.csv"
    )
    assert result.task_name == "test"
    assert result.data_version == "1.5"
    assert result.code_version == "1.0.5"
    assert result.comment == "Only essential fields"
    assert result.created_by == "janedoe"
    assert result.last_update == datetime(2024, 1, 1, 0, 1, 30, tzinfo=timezone.utc)


def test_filter_multiple_resources(test_resources):
    repo = test_resources

    # test if specific resource is loaded correctly
    result = repo.get_resource_info(name="SampleRegion")

    assert len(result) == 2
    assert result[0].name == "SampleRegion"


def test_read_data_for_task(test_resources):
    repo = test_resources
    result = repo.get_dataframe_for_task("SampleRegion", data_version="1.5")

    # Sample data conforming to the specified schema
    expected_data = {
        "position": [0, 1, 2, 3],
        "code": ["AT", "DE", "UK", "DK"],
        "prefixed_id": ["ID001", "ID002", "ID003", "ID004"],
        "parent_id": ["PID001", "PID001", "PID002", "PID003"],
        "level": ["0", "1", "1", "2"],
        "name": ["Alpha", "Beta", "Gamma", "Delta"],
        "description": ["First entry", "Second entry", "Last entry", "Fourth entry"],
    }
    expected_result = pd.DataFrame(expected_data)
    expected_result["position"] = expected_result["position"].astype(int)

    pd.testing.assert_frame_equal(result, expected_result)


def test_write_csv_data(setup_empty_csv_repository):
    # this test defines a pandas dataframe that is then stored as csv file
    # using the resources.write_data method
    # This then results in an updated resources table
    repo = setup_empty_csv_repository

    # Define a DataFrame to write, adhering to the Footprint schema
    data_to_add = pd.DataFrame(
        {
            "flow_code": ["FC100"],
            "description": ["Emission from transportation"],
            "unit_reference": ["per vehicle"],
            "region_code": ["US"],
            "value": [123.45],
            "unit_emission": ["tonnes CO2eq"],
        }
    )

    name = "new_resource"
    last_updated = datetime(2024, 1, 1, 0, 5, 30, tzinfo=timezone.utc)

    # Writing the DataFrame to CSV using the repository method
    repo.write_dataframe_for_task(
        name=name,
        data=data_to_add,
        task_name="new_task",
        stage="processed",
        location=f"data/{name}.csv",
        schema_name="Footprint",
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        last_update=last_updated,
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )

    # Verification step to ensure the data has been added
    assert repo.get_resource_info(name=name).name == name
    assert repo.get_resource_info(name=name).last_update == last_updated
    # Read the data back from the resource to verify it matches the original DataFrame
    retrieved_data = repo.get_dataframe_for_task(name=name)

    assert (retrieved_data.columns == data_to_add.columns).all()

    # Compare the original DataFrame with the retrieved one
    pd.testing.assert_frame_equal(
        data_to_add, retrieved_data.reset_index(drop=True), check_dtype=False
    )


def test_write_load_matrix_data(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    # Define the MultiIndex for columns
    columns_tuples = [
        ("New York", "Sales", "kg", 2023),
        ("New York", "Sales", "kg", 2024),
        ("Los Angeles", "Sales", "kg", 2023),
        ("Los Angeles", "Sales", "kg", 2024),
    ]

    columns = pd.MultiIndex.from_tuples(
        columns_tuples, names=["location", "activity", "unit", "time"]
    )

    # Define the MultiIndex for rows
    index_tuples = [
        ("New York", "Apples", "kg", 2023),
        ("New York", "Oranges", "kg", 2023),
        ("Los Angeles", "Apples", "kg", 2023),
        ("Los Angeles", "Oranges", "kg", 2023),
        ("New York", "Apples", "kg", 2024),
        ("New York", "Oranges", "kg", 2024),
        ("Los Angeles", "Apples", "kg", 2024),
        ("Los Angeles", "Oranges", "kg", 2024),
    ]

    row_index = pd.MultiIndex.from_tuples(
        index_tuples, names=["location", "product", "unit", "time"]
    )

    # Create the DataFrame with random data
    data = np.random.rand(len(index_tuples), len(columns))

    df = pd.DataFrame(data, index=row_index, columns=columns)

    # Save the DataFrame
    name = "new_resource"
    # Writing the DataFrame to CSV using the repository method
    repo.write_dataframe_for_task(
        name=name,
        data=df,
        task_name="new_task",
        stage="processed",
        location=f"data/{name}.h5",
        schema_name=schemas.A_Matrix,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )

    # Verification step to ensure the data has been added
    assert repo.get_resource_info(name=name).name == name
    # Read the data back from the resource to verify it matches the original DataFrame
    retrieved_data = repo.get_dataframe_for_task(name=name)

    assert (retrieved_data.columns == df.columns).all()

    # Compare the original DataFrame with the retrieved one
    pd.testing.assert_frame_equal(df, retrieved_data)


def test_location_written_correctly_to_csv(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    # Define the expected path using `Path` for platform-independent path handling
    expected_location_in_csv = str(
        Path("clean") / "{task_name}" / "{version}" / "{resource_name}.csv"
    )
    expected_last_update = "2024-07-01 17:55:13-07:00"

    resource = schemas.DataResource(
        name="data",
        task_name="task1",
        stage="clean",
        location="clean/{task_name}/{version}/{resource_name}.csv",
        schema_name=schemas.Footprint,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        last_update=datetime.fromisoformat("2024-07-01T17:55:13-07:00"),
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )

    repo.add_or_update_resource_list(resource)

    all_resources = pd.read_csv(repo.resources_list_path)

    # Normalize the path separators for comparison
    location_in_csv = os.path.normpath(
        all_resources[schemas.DataResource.names.location][0]
    )
    expected_location_in_csv = os.path.normpath(expected_location_in_csv)

    last_update_in_csv = all_resources[schemas.DataResource.names.last_update][0]

    # Assert the normalized paths
    assert (
        location_in_csv == expected_location_in_csv
    ), f"Expected {expected_location_in_csv}, but got {location_in_csv}"
    assert (
        last_update_in_csv == expected_last_update
    ), f"Expected last update {expected_last_update}, but got {last_update_in_csv}"


def test_last_update_written_correctly_to_csv(setup_empty_csv_repository):

    repo = setup_empty_csv_repository

    resource = schemas.DataResource(
        name="data",
        task_name="task1",
        stage="clean",
        location="clean/{task_name}/{version}/{resource_name}.csv",
        schema_name=schemas.Footprint,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )

    repo.add_or_update_resource_list(resource)

    all_resources = pd.read_csv(repo.resources_list_path)

    last_update_in_csv = all_resources[schemas.DataResource.names.last_update]

    matching = re.compile("\d+-\d+-\d+ \d+:\d+:\d+\.\d+\w?")
    assert matching.match(last_update_in_csv[0]) is not None


def test_version_change_reflected():

    expected_location = str(
        Path("tests").absolute() / "clean" / "task1" / "1.0" / "data.csv"
    )
    resource = schemas.DataResource(
        name="data",
        task_name="task1",
        stage="clean",
        location="{stage}/{task_name}/{version}/{resource_name}.csv",
        schema_name=schemas.Footprint,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )
    assert expected_location == resource.location

    resource.data_version = "1.7"

    new_expected_location = str(
        Path("tests").absolute() / "clean" / "task1" / "1.7" / "data.csv"
    )
    assert new_expected_location == resource.location


def test_load_with_bonsai_classification_easy_location(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    data = {
        "time": [1995, 1996, 2010, 2011, 2012, 2022, 2023, 1998, 1999],
        "location": [
            "0830",
            "0004",
            "0488",
            "0028",
            "0830",
            "0001",
            "0008",
            "0720",
            "0036",
        ],
        "product": [
            "08111133",
            "08111133",
            "20144340",
            "20144340",
            "20144340",
            "20143271",
            "20143271",
            "20132433",
            "20132433",
        ],
        "indicator": [
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PRODQNT",
            "PRODQNT",
            "PRODQNT",
            "PRODQNT",
        ],
        "value": [
            0.0,
            0.0,
            None,
            None,
            None,
            18985646.0,
            26147117.0,
            808695030.0,
            911342280.0,
        ],
        "unit": ["kg", "kg", "kg", "kg", "kg", "kg", "kg", "kg SO2", "kg SO2"],
        "flag": [None, None, None, ":C", ":C", None, None, None, None],
        "source": [
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
        ],
    }

    df = pd.DataFrame(data)

    repo.write_dataframe_for_task(
        name="testing_data",
        data=df,
        task_name="new_task",
        stage="processed",
        location="data/test.csv",
        schema_name="PRODCOMProductionVolume",
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        last_update=date.today(),
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )

    bonsai_df, unmapped_values = repo.load_with_bonsai_classification(
        name="testing_data"
    )

    expected_data = {
        "time": [1995, 1996, 1998, 1999, 2010, 2011, 2012, 2022, 2023],
        "location": ["AS", "DE", "CN", "CH", "GY", "NO|AX", "AS", "FR|MC|MF", "DK"],
        "product": [
            "fi_15120",
            "fi_15120",
            "20132433",
            "20132433",
            "fi_34150",
            "fi_34150",
            "fi_34150",
            "fi_34140",
            "fi_34140",
        ],
        "unit": ["kg", "kg", "kg SO2", "kg SO2", "kg", "kg", "kg", "kg", "kg"],
        "value": [0.0, 0, 808695030, 911342280, 0, 0, 0, 18985646, 26147117],
        "indicator": [
            "PQNTBASE",
            "PQNTBASE",
            "PRODQNT",
            "PRODQNT",
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PRODQNT",
            "PRODQNT",
        ],
        "flag": ["", "", "", "", "", ":C", ":C", "", ""],
        "source": 9 * ["prodcom"],
    }

    expected_df = pd.DataFrame(expected_data)

    expected_df.sort_values(by="time", inplace=True, ignore_index=True)
    bonsai_df.sort_values(by="time", inplace=True, ignore_index=True)

    # Compare DataFrames
    pd.testing.assert_frame_equal(
        bonsai_df, expected_df, check_like=True, check_dtype=False
    )


def test_convert_conc_pair(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    data = {
        "time": [
            1990,
            1991,
            2018,
            2019,
            1990,
            1991,
            2021,
            2019,
            2020,
            2021,
            2022,
            2017,
            2000,
            2001,
            2001,
            2001,
            2017,
            2017,
            2016,
            2016,
            2016,
        ],
        "location": [
            "004",
            "004",
            "004",
            "004",
            "004",
            "004",
            "031",
            "031",
            "031",
            "031",
            "020",
            "040",
            "008",
            "008",
            "008",
            "008",
            "008",
            "008",
            "004",
            "004",
            "004",
        ],
        "activity": [
            "01",
            "01",
            "04",
            "04",
            "01",
            "01",
            "0889E",
            "0889H",
            "0889H",
            "0889H",
            "01",
            "01",
            "1211",
            "1211",
            "01",
            "01",
            "01",
            "01",
            "015PH",
            "016HY",
            "015PH",
        ],
        "product": [
            "0110",
            "0110",
            "0311",
            "0311",
            "3000",
            "3000",
            "7000",
            "7000",
            "7000",
            "7000",
            "6200",
            "7000G",
            "4670",
            "4670",
            "8000T",
            "4652",
            "5220",
            "5222",
            "0360",
            "0360",
            "5232",
        ],
        "value": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8.2,
            9.1,
            10.2,
            11.84,
            12.091,
            13,
            14,
            14,
            14,
            1,
            2,
            1,
            1,
            10,
        ],
        "unit": [
            "TN",
            "TN",
            "TN",
            "TN",
            "TJ",
            "TJ",
            "GWHR",
            "GWHR",
            "GWHR",
            "GWHR",
            "TJ",
            "GWHR",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
        ],
        "flag": [
            "A",
            "A",
            "E",
            "E",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
        ],
        "conversion_factor": [
            0.0258,
            0.0258,
            0.0282,
            0.0282,
            1.0,
            1.0,
            3.6,
            3.6,
            3.6,
            3.6,
            1.0,
            3.6,
            0.043,
            0.043,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            2.0,
        ],
    }

    df = pd.DataFrame(data)
    transformed_data, unmapped_values = repo.convert_dataframe_to_bonsai_classification(
        df, original_schema=schemas.UNdataEnergyStatistic
    )

    expected_data = {
        "time": [
            1990,
            1990,
            1991,
            1991,
            2000,
            2001,
            2001,
            2001,
            2016,
            2016,
            2017,
            2017,
            2018,
            2019,
            2019,
            2020,
            2021,
            2021,
            2022,
        ],
        "location": [
            "AF",
            "AF",
            "AF",
            "AF",
            "AL",
            "AL",
            "AL",
            "AL",
            "AF",
            "AF",
            "AL",
            "AT",
            "AF",
            "AF",
            "AZ",
            "AZ",
            "AZ",
            "AZ",
            "AD",
        ],
        "activity": [
            "ai_051_1",
            "ai_1920_6",
            "ai_051_1",
            "ai_1920_6",
            "ai_2410",
            "ai_1920_10",
            "ai_2410",
            "ai_3530_3",
            "ai_3510_7",
            "ai_3510_7",
            "ai_1920_1",
            "ai_3510_8",
            "oa_exp",
            "oa_exp",
            "ai_2815_2",
            "ai_2815_2",
            "ai_2815_2",
            "ai_2815_3",
            "at_3821_85|at_3821_84",
        ],
        "product": [
            "fi_11010_1",
            "fi_12020",
            "fi_11010_1",
            "fi_12020",
            "fi_33360",
            "fi_3331_1",
            "fi_33360",
            "fi_1730",
            "fi_17200_3",
            "fi_35491",
            "fi_35491",
            "fi_17100_8",
            "fi_33100",
            "fi_33100",
            "fi_17100",
            "fi_17100",
            "fi_17100",
            "fi_17100",
            "fi_39910_2|fi_39910_1",
        ],
        "value": [
            1.0,
            5.0,
            2.0,
            6.0,
            13.0,
            14.0,
            14.0,
            14.0,
            2.0,
            10.0,
            3.0,
            12.091,
            3.0,
            4.0,
            8.2,
            9.1,
            10.2,
            7.0,
            11.84,
        ],
        "unit": [
            "TN",
            "TJ",
            "TN",
            "TJ",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
            "TN",
            "GWHR",
            "TN",
            "TN",
            "GWHR",
            "GWHR",
            "GWHR",
            "GWHR",
            "TJ",
        ],
        "flag": [
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "A",
            "E",
            "E",
            "A",
            "A",
            "A",
            "A",
            "A",
        ],
        "conversion_factor": [
            0.0258,
            1.0,
            0.0258,
            1.0,
            0.043,
            1.0,
            0.043,
            1.0,
            1.0,
            2.0,
            1.0,
            3.6,
            0.0282,
            0.0282,
            3.6,
            3.6,
            3.6,
            3.6,
            1.0,
        ],
        "accounttype": [
            "supply",
            "supply",
            "supply",
            "supply",
            "use_transformation",
            "supply",
            "use_transformation",
            "supply",
            "supply",
            "supply",
            "supply",
            "supply",
            "trade",
            "trade",
            "supply",
            "supply",
            "supply",
            "supply",
            "supply",
        ],
    }

    expected_df = pd.DataFrame(expected_data)

    transformed_data.sort_values(
        by=["time", "location", "activity"], inplace=True, ignore_index=True
    )
    pd.testing.assert_frame_equal(expected_df, transformed_data)


def test_load_with_classification(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    data = {
        "time": [1995, 1996, 1998, 1999, 2010, 2011, 2012, 2022, 2023],
        "location": ["001", "001", "005", "005", "005", "001", "001", "009", "009"],
        "product": [
            "08111133",
            "08111133",
            "20144340",
            "20144340",
            "20144340",
            "20143271",
            "20143271",
            "20132433",
            "20132433",
        ],
        "indicator": [
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PRODQNT",
            "PRODQNT",
            "PRODQNT",
            "PRODQNT",
        ],
        "value": [0, 0, None, None, None, 18985646, 26147117, 808695030, 911342280],
        "unit": ["kg", "kg", "kg", "kg", "kg", "kg", "kg", "kg SO2", "kg SO2"],
        "flag": [None, None, None, ":C", ":C", None, None, None, None],
        "source": 9 * ["prodcom"],
    }

    df = pd.DataFrame(data)

    repo.write_dataframe_for_task(
        name="testing_data",
        data=df,
        task_name="new_task",
        stage="processed",
        location="data/test.csv",
        schema_name="PRODCOMProductionVolume",
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        last_update=date.today(),
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )

    bonsai_df, unmapped_values = repo.load_with_classification(
        classifications={"flowobject": "bonsai", "location": "bonsai"},
        name="testing_data",
    )

    expected_data = df.copy()
    expected_data["value"] = df.value.fillna(0)
    expected_data["flag"] = df.flag.fillna("")
    expected_data["product"] = [
        "fi_15120",
        "fi_15120",
        "fi_34150",
        "fi_34150",
        "fi_34150",
        "fi_34140",
        "fi_34140",
        "20132433",
        "20132433",
    ]
    # NOTE: location would be converted if the zeroes are removed

    expected_df = pd.DataFrame(expected_data)
    expected_df.sort_values(by="time", inplace=True, ignore_index=True)
    bonsai_df.sort_values(by="time", inplace=True, ignore_index=True)

    expected_df["time"] = expected_df["time"].astype("int64")
    bonsai_df["time"] = bonsai_df["time"].astype("int64")

    # Compare DataFrames
    pd.testing.assert_frame_equal(bonsai_df, expected_df, check_like=True)


def test_harmonize_with_resource(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    data = {
        "time": [1995, 1996, 1998, 1999, 2010, 2011, 2012, 2022, 2023],
        "location": ["FRA", "FRA", "GRC", "GRC", "ITA", "ITA", "ITA", "FRA", "FRA"],
        "product": [
            "C_STON",
            "C_STON",
            "C_CHEM",
            "C_CHEM",
            "C_CHEM",
            "C_CHEM",
            "C_CHEM",
            "C_CHEM",
            "C_CHEM",
        ],
        "unit": ["kg", "kg", "kg SO2", "kg SO2", "kg", "kg", "kg", "kg", "kg"],
        "value": [
            0.0,
            0.0,
            808695030.0,
            911342280.0,
            0.0,
            0.0,
            0.0,
            18985646.0,
            26147117.0,
        ],
        "indicator": [
            "PQNTBASE",
            "PQNTBASE",
            "PRODQNT",
            "PRODQNT",
            "PQNTBASE",
            "PQNTBASE",
            "PQNTBASE",
            "PRODQNT",
            "PRODQNT",
        ],
        "flag": [None, None, None, None, None, ":C", ":C", None, None],
        "source": [
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
            "prodcom",
        ],
    }

    df = pd.DataFrame(data)

    df_before_2000 = df[df["time"] < 2000].reset_index(drop=True)
    df_after_2000 = df[df["time"] >= 2000].reset_index(drop=True)

    repo.write_dataframe_for_task(
        name="testing_data",
        data=df_before_2000,
        task_name="new_task",
        stage="processed",
        location=f"data/test.csv",
        schema_name="ProductionVolumes_uncertainty",
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        last_update=date.today(),
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )

    repo.harmonize_with_resource(df_after_2000, name="testing_data")

    resource = repo.get_latest_version(name="testing_data")
    assert resource.data_version == "1.1"
    result = repo.get_dataframe_for_task(
        name=resource.name, data_version=resource.data_version
    )

    # Create temporary files for comparison
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".csv"
    ) as bonsai_file, tempfile.NamedTemporaryFile(
        delete=False, suffix=".csv"
    ) as expected_file:

        bonsai_path = bonsai_file.name
        expected_path = expected_file.name

        # Write DataFrames to temporary CSV files
        df.to_csv(bonsai_path, index=False)
        result.to_csv(expected_path, index=False)

    # Read the files back into DataFrames
    bonsai_df = pd.read_csv(bonsai_path)
    expected_df = pd.read_csv(expected_path)

    # Clean up temporary files
    os.remove(bonsai_path)
    os.remove(expected_path)

    # Compare DataFrames
    pd.testing.assert_frame_equal(bonsai_df, expected_df, check_like=True)


def test_available_resources_not_dict_for_non_existing_csv(tmp_path):
    os.environ["BONSAI_HOME"] = str(tmp_path.absolute())
    os.environ["DATAIO_ROOT"] = str(tmp_path.absolute())
    test_config = Config(current_task_name="test")
    test_config.current_code_version = "test"
    repo = test_config.resource_repository
    resource = schemas.DataResource(
        name="data",
        task_name="task1",
        stage="clean",
        location="clean/{task_name}/{version}/{resource_name}.csv",
        schema_name=schemas.Footprint,
        data_flow_direction="output",
        data_version="1.0",
        code_version="1.1",
        last_update=datetime.fromisoformat("2024-07-01T17:55:13-07:00"),
        comment="Newly added data for emissions",
        created_by="developer",
        dag_run_id="run200",
    )
    repo.resource_exists(resource)


def test_convert_units(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    data = {
        "unit": ["kWh", "USD", "kg", "g", "m"],
        "value": [100, 50, 200, 500, 2],
        "other_column": ["A", "B", "C", "D", "E"],
    }
    df = pd.DataFrame(data)

    # List of target units for conversion
    target_units = ["tonne", "MWh", "m"]

    result = repo.convert_units(df, target_units)

    expected_data = {
        "unit": ["MWh", "USD", "tonne", "tonne", "m"],
        "value": [0.1, 50, 0.200, 0.0005, 2],
        "other_column": ["A", "B", "C", "D", "E"],
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result, expected_df)


def test_convert_currencies(setup_empty_csv_repository):
    repo = setup_empty_csv_repository

    data = {
        "unit": ["USD_2020", "EUR_2020", "GBP_2017", "kg"],
        "value": [50, 40, 30, 2000],
        "year": [2016, 2016, 2016, 2016],  # Source year
    }
    df = pd.DataFrame(data)

    # List of target units for conversion
    target_units = ["EUR_2020", "tonne"]

    # Convert units between years
    result = repo.convert_units(df, target_units)

    expected_data = {
        "unit": ["EUR_2020", "EUR_2020", "EUR_2020", "tonne"],
        "value": [57.109805447469995, 40.0, 41.24949183165757, 2.0],
        "year": [2016, 2016, 2016, 2016],  # Source year
    }
    expected_df = pd.DataFrame(expected_data)
    # Display the result

    pd.testing.assert_frame_equal(result, expected_df)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing, cleaned up automatically."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def test_csvresource_repository_returns_resource_repo(temp_dir):
    """
    Test that CSVResourceRepository returns a ResourceRepository object
    and initializes the correct 'local' storage settings.
    """
    table_name = "test_resources"
    repo = CSVResourceRepository(db_path=temp_dir, table_name=table_name)

    # Check type
    assert isinstance(
        repo, ResourceRepository
    ), "CSVResourceRepository should return a ResourceRepository instance."

    # Check attributes
    assert (
        repo.db_path == temp_dir
    ), f"Expected db_path to be {temp_dir}, got {repo.db_path} instead."
    assert (
        repo.table_name == table_name
    ), f"Expected table_name to be {table_name}, got {repo.table_name} instead."

    # Since storage_method='local', verify it's set to local
    assert (
        repo.load_storage_method == "local"
    ), "Expected load_storage_method to be 'local'."
    assert (
        repo.save_storage_method == "local"
    ), "Expected save_storage_method to be 'local'."

    # Check that the CSV file is created
    expected_csv_path = temp_dir / f"{table_name}.csv"
    assert (
        expected_csv_path.exists()
    ), f"CSV file {expected_csv_path} should have been created but was not."


def test_coke_slimmed_inline(setup_empty_csv_repository):
    """
    Inline version of slimmed coke: generate random ‘use’ and ‘supply’ tables
    and write them, then verify via get_dataframe_for_task.
    """
    # 1) Arrange: set environment so DataResource paths resolve under tests/

    repo = setup_empty_csv_repository

    # 2) Create two DataResource entries (use & supply) without writing files
    use_res = schemas.DataResource(
        name="ppf_coke_use",
        task_name="build_ppf_coke",
        schema_name="Use_uncertainty",
        location="build/build_ppf_coke/v0.0.0/ppf_coke_use.csv",
        stage="build",
        data_flow_direction="output",
        data_version="v0.0.0",
        code_version="v0.0.0",
        last_update="2024-10-07",
    )
    supply_res = schemas.DataResource(
        name="ppf_coke_supply",
        task_name="build_ppf_coke",
        schema_name="Supply_uncertainty",
        location="build/build_ppf_coke/v0.0.0/ppf_coke_supply.csv",
        stage="build",
        data_flow_direction="output",
        data_version="v0.0.0",
        code_version="v0.0.0",
        last_update="2024-10-07",
    )
    repo.add_or_update_resource_list(use_res)
    repo.add_or_update_resource_list(supply_res)

    # 3) Act: generate dummy Use_uncertainty DataFrame inline
    np.random.seed(0)
    n_rows = 5
    use_data = {
        "location": np.random.choice(["DK", "NO", "SE", "FI", "DE"], size=n_rows),
        "product": np.random.choice(["fi_33100", "fi_33110"], size=n_rows),
        "activity": np.random.choice(["ai_1910", "ai_1911"], size=n_rows),
        "unit": ["t/yr"] * n_rows,
        "value": np.random.uniform(1000, 5000, size=n_rows),
        "associated_product": [None] * n_rows,
        "flag": [None] * n_rows,
        "time": np.random.choice([2018, 2019, 2020, 2021, 2022], size=n_rows),
        "product_origin": np.random.choice(["fi_33100", "fi_33110"], size=n_rows),
    }
    use_df = pd.DataFrame(use_data)
    use_df["product_type"] = "use"
    use_df["account_type"] = None

    # 4) Write use_df to the repository
    use_meta = repo.get_resource_info(
        name="ppf_coke_use", task_name="build_ppf_coke", data_flow_direction="output"
    )
    repo.write_dataframe_for_task(
        data=use_df,
        name=use_meta.name,
        stage=use_meta.stage,
        task_name=use_meta.task_name,
        location=f"{use_meta.stage}/{use_meta.task_name}/{use_meta.data_version}/{use_meta.name}.csv",
        data_version=use_meta.data_version,
        schema_name=use_meta.schema_name,
        code_version=use_meta.code_version,
        data_flow_direction=use_meta.data_flow_direction,
    )

    # 5) Generate dummy Supply_uncertainty DataFrame inline
    np.random.seed(1)
    supply_data = {
        "location": np.random.choice(["DK", "NO", "SE", "FI", "DE"], size=n_rows),
        "product": np.random.choice(["fi_33100", "fi_33110"], size=n_rows),
        "activity": np.random.choice(["ai_1910", "ai_1911"], size=n_rows),
        "unit": ["t/yr"] * n_rows,
        "value": np.random.uniform(2000, 6000, size=n_rows),
        "product_destination": [None] * n_rows,
        "associated_product": [None] * n_rows,
        "flag": [None] * n_rows,
        "time": np.random.choice([2018, 2019, 2020, 2021, 2022], size=n_rows),
    }
    supply_df = pd.DataFrame(supply_data)
    supply_df["product_type"] = np.random.choice(
        ["determining-product", "joint-by-product", "supply"], size=n_rows
    )
    supply_df["account_type"] = None

    # 6) Write supply_df to the repository
    supply_meta = repo.get_resource_info(
        name="ppf_coke_supply", task_name="build_ppf_coke", data_flow_direction="output"
    )
    repo.write_dataframe_for_task(
        data=supply_df,
        name=supply_meta.name,
        stage=supply_meta.stage,
        task_name=supply_meta.task_name,
        location=f"{supply_meta.stage}/{supply_meta.task_name}/{supply_meta.data_version}/{supply_meta.name}.csv",
        data_version=supply_meta.data_version,
        schema_name=supply_meta.schema_name,
        code_version=supply_meta.code_version,
        data_flow_direction=supply_meta.data_flow_direction,
    )

    # 7) Assert: 'use' table exists and has expected columns & values
    out_use = repo.get_dataframe_for_task(
        name="ppf_coke_use",
        task_name="build_ppf_coke",
        stage="build",
        data_flow_direction="output",
    )
    assert isinstance(out_use, pd.DataFrame)
    for col in [
        "location",
        "product",
        "activity",
        "unit",
        "value",
        "time",
        "product_type",
    ]:
        assert col in out_use.columns
    assert (out_use["product_type"] == "use").all()

    # 8) Assert: 'supply' table exists and includes required product_type
    out_supply = repo.get_dataframe_for_task(
        name="ppf_coke_supply",
        task_name="build_ppf_coke",
        stage="build",
        data_flow_direction="output",
    )
    assert isinstance(out_supply, pd.DataFrame)
    for col in [
        "location",
        "product",
        "activity",
        "unit",
        "value",
        "time",
        "product_type",
    ]:
        assert col in out_supply.columns
    assert (
        out_supply["product_type"]
        .isin(["determining-product", "joint-by-product"])
        .any()
    )
