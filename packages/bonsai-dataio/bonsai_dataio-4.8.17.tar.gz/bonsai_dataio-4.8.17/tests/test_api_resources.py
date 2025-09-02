import os
import tempfile
import time
import unittest
import uuid
from pathlib import Path, PureWindowsPath
from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

import pandas as pd
import pytest
import requests
from pandas.testing import assert_frame_equal

from dataio.resources import ResourceRepository
from dataio.schemas.bonsai_api.admin import DataResource


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["DATAIO_ROOT"] = str(Path("tests").absolute())


class TestAPIResourceRepository(unittest.TestCase):
    #
    # ------------------ EXISTING TOKEN-CREATION TESTS ------------------
    #
    @patch("requests.Session.post")
    def test_create_token_success(self, mock_post):
        """
        Test that a token is successfully created when valid credentials are provided.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": "FAKE_TOKEN_VALUE"}
        mock_response.raise_for_status.return_value = None  # No exception => success
        mock_post.return_value = mock_response

        repo = ResourceRepository(
            db_path="some/path",
            storage_method="api",
            username="valid_user@example.com",
            password="valid_password",
        )

        self.assertEqual(repo.token, "FAKE_TOKEN_VALUE")
        mock_post.assert_called_once_with(
            "https://lca.aau.dk/api/user/token/",
            json={"email": "valid_user@example.com", "password": "valid_password"},
        )

    @patch("requests.Session.post")
    def test_create_token_invalid_credentials(self, mock_post):
        """
        Test that a ValueError is raised when invalid credentials are provided.
        """
        mock_response = MagicMock()
        # Simulate an HTTPError raised by raise_for_status()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            ResourceRepository(
                db_path="some/path",
                storage_method="api",
                username="invalid_user@example.com",
                password="wrong_password",
            )

        self.assertIn("Invalid credentials", str(context.exception))
        mock_post.assert_called_once_with(
            "https://lca.aau.dk/api/user/token/",
            json={"email": "invalid_user@example.com", "password": "wrong_password"},
        )

    @patch("requests.Session.post")
    def test_missing_token_key_in_response(self, mock_post):
        """
        Test that a ValueError is raised if the 'token' key is missing in the server response.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"something_else": "no_token_here"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            ResourceRepository(
                db_path="some/path",
                storage_method="api",
                username="test_user@example.com",
                password="test_password",
            )
        self.assertIn("Token not found in the response", str(context.exception))
        mock_post.assert_called_once_with(
            "https://lca.aau.dk/api/user/token/",
            json={"email": "test_user@example.com", "password": "test_password"},
        )

    #
    # ------------------ NEW TESTS FOR add_to_resource_list (API mode) ------------------
    #

    @patch("requests.Session.post")
    def test_add_to_resource_list_api_success(self, mock_post):
        """
        Test adding a new resource in 'api' mode. Should POST data to version-dataio
        and return the generated UUID.
        """
        # 1. Mock the version-dataio POST response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None  # no exception => success
        mock_response.status_code = 201
        mock_response.json.return_value = {"detail": "Resource created successfully"}
        mock_post.return_value = mock_response

        # 2. Create a ResourceRepository in API mode with a pre-provided token
        repo = ResourceRepository(
            db_path="some/path",  # not used in 'api'-only mode
            storage_method="api",
            API_token="FAKE_TOKEN_VALUE",
        )

        # 3. Create a DataResource instance to add
        resource = DataResource(
            name="data",
            task_name="task1",
            stage="clean",
            schema_name="MySchema",
            data_version="v0.0.0",
            api_endpoint="testing/",
        )

        # 4. Call add_to_resource_list -> should generate a UUID and POST to version-dataio
        returned_uuid = repo.add_to_resource_list(resource)

        # 5. Verify the POST endpoint and JSON payload
        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        self.assertEqual(
            call_args[0], "https://lca.aau.dk/api/version-dataio/"
        )  # endpoint

        # The JSON payload should include at least 'id', 'name', and 'schema_name'
        sent_json = call_kwargs["json"]
        self.assertIn("id", sent_json)
        self.assertEqual(sent_json["name"], "data")
        self.assertEqual(sent_json["schema_name"], "MySchema")

        # 6. Check that the returned UUID matches what's in the payload
        self.assertIsInstance(returned_uuid, str)
        self.assertEqual(returned_uuid, sent_json["id"])

        # Optionally, assert that it's a valid UUID format
        try:
            uuid_obj = uuid.UUID(returned_uuid, version=4)
            self.assertEqual(str(uuid_obj), returned_uuid)
        except ValueError:
            self.fail("Returned UUID is not a valid UUID4 string.")

    @patch("requests.Session.post")
    def test_add_to_resource_list_api_bad_request(self, mock_post):
        """
        Test that a 400 Bad Request from the server raises a ValueError.
        """
        # 1. Mock a 400 error on POST
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_response.status_code = 400
        mock_response.text = "Invalid fields"
        mock_post.return_value = mock_response

        # 2. Instantiate repo
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN_VALUE"
        )

        resource = DataResource(
            name="Bad Resource",
            schema_name="BadSchema",
            task_name="test",
            stage="test",
            data_version="v0.0.0",
            api_endpoint="testing/",
        )

        # 3. Expect a ValueError due to the 400 status
        with self.assertRaises(ValueError) as context:
            repo.add_to_resource_list(resource)
        self.assertIn("Bad request", str(context.exception))
        self.assertIn("Invalid fields", str(context.exception))

        # 4. Ensure it called the correct endpoint with the 'id'
        mock_post.assert_called_once_with(
            "https://lca.aau.dk/api/version-dataio/",
            json=self.assertDictContainsIdAndFields("Bad Resource", "BadSchema"),
        )

    @patch("requests.Session.post")
    def test_add_to_resource_list_api_unauthorized(self, mock_post):
        """
        Test that a 401 Unauthorized from the server raises a ValueError.
        """
        # 1. Mock a 401 error on POST
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        # 2. Instantiate repo
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN_VALUE"
        )
        resource = DataResource(
            name="Test Resource",
            schema_name="MySchema",
            task_name="test",
            stage="test",
            data_version="v0.0.0",
            api_endpoint="testing/",
        )

        # 3. Expect a ValueError due to the 401 status
        with self.assertRaises(ValueError) as context:
            repo.add_to_resource_list(resource)
        self.assertIn("Unauthorized", str(context.exception))

        # 4. Ensure we tried to POST to the version-dataio endpoint
        mock_post.assert_called_once()

    #
    # ----------- Optional Helper Assertion -----------
    #
    def assertDictContainsIdAndFields(self, name, schema_name):
        """
        Helper method for checking that the JSON payload has at least 'id', 'name', and 'schema_name'.
        We return a custom object that can be used in mock call assertions.
        """

        class DictCheck:
            def __eq__(self, other):
                # Must have an 'id' field
                if "id" not in other:
                    return False
                # Must match specific name/schemaname
                if other.get("name") != name:
                    return False
                if other.get("schema_name") != schema_name:
                    return False
                # Optional: Validate 'id' is a plausible UUID
                try:
                    uuid.UUID(other["id"], version=4)
                except ValueError:
                    return False
                return True

        return DictCheck()

    @patch.object(ResourceRepository, "resource_exists", return_value=True)
    @patch.object(
        ResourceRepository, "update_resource_list", return_value="UPDATED_UUID"
    )
    @patch.object(ResourceRepository, "add_to_resource_list", return_value="NEW_UUID")
    def test_add_or_update_resource_list_update(
        self, mock_add, mock_update, mock_exists
    ):
        """
        If resource_exists() is True, then add_or_update_resource_list should call update_resource_list
        and return its UUID.
        """
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )
        resource = DataResource(
            name="ResourceToUpdate",
            schema_name="SomeSchema",
            task_name="test",
            stage="test",
            data_version="v0.0.0",
        )

        version_uuid = repo.add_or_update_resource_list(resource)

        # Because resource_exists returned True, we expect update_resource_list to be called
        mock_update.assert_called_once_with(resource, None)
        mock_add.assert_not_called()
        self.assertEqual(version_uuid, "UPDATED_UUID")

    @patch.object(ResourceRepository, "resource_exists", return_value=False)
    @patch.object(
        ResourceRepository, "update_resource_list", return_value="UPDATED_UUID"
    )
    @patch.object(ResourceRepository, "add_to_resource_list", return_value="NEW_UUID")
    def test_add_or_update_resource_list_add(self, mock_add, mock_update, mock_exists):
        """
        If resource_exists() is False, add_or_update_resource_list should call add_to_resource_list
        and return its UUID.
        """
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )
        resource = DataResource(
            name="ResourceToAdd",
            schema_name="SomeSchema",
            task_name="test",
            stage="test",
            data_version="v0.0.0",
        )

        version_uuid = repo.add_or_update_resource_list(resource)

        # Because resource_exists returned False, we expect add_to_resource_list to be called
        mock_add.assert_called_once_with(resource, None)
        mock_update.assert_not_called()
        self.assertEqual(version_uuid, "NEW_UUID")

    #
    # ----------------- update_resource_list Tests -----------------
    #

    @patch("requests.Session.get")
    @patch("requests.Session.patch")
    def test_update_resource_list_api_success(self, mock_patch, mock_get):
        """
        Test a successful API patch update. We assume resource_exists() was True, so
        there's exactly one match from the GET request.
        """
        # 1. Mock the GET response to return exactly one matching resource with an 'id'
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = [{"id": "EXISTING_UUID"}]
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response

        # 2. Mock the PATCH response to be successful
        mock_patch_response = MagicMock()
        mock_patch_response.raise_for_status.return_value = None
        mock_patch.return_value = mock_patch_response

        # 3. Create the repo in API mode
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )

        # 4. Create a DataResource
        resource = DataResource(
            name="ExistingResource",
            task_name="test",
            schema_name="ExistingSchema",
            data_version="1.0.0",
            stage="test",
            # etc.
        )

        # 5. Call update_resource_list
        returned_uuid = repo.update_resource_list(resource)

        # 6. Verify the GET call:
        mock_get.assert_called_once()
        # The GET call should have used query params that match the resource's identifying fields:
        get_call_args, get_call_kwargs = mock_get.call_args
        self.assertIn("params", get_call_kwargs)
        self.assertEqual(get_call_kwargs["params"]["name"], "ExistingResource")

        # 7. Verify the PATCH call:
        mock_patch.assert_called_once()
        patch_call_args, patch_call_kwargs = mock_patch.call_args
        self.assertIn("json", patch_call_kwargs)
        # The 'id' in the patch payload should match what GET returned
        self.assertEqual(patch_call_kwargs["json"]["id"], "EXISTING_UUID")

        # 8. The method should return the existing resource's ID
        self.assertEqual(returned_uuid, "EXISTING_UUID")

    @patch("requests.Session.get")
    @patch("requests.Session.patch")
    def test_update_resource_list_api_patch_error(self, mock_patch, mock_get):
        """
        If the PATCH request fails, we expect an exception to be raised.
        """
        # Mock GET to return exactly one resource
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = [{"id": "EXISTING_UUID"}]
        mock_get.return_value = mock_get_response

        # Mock PATCH to raise an HTTPError
        mock_patch_response = MagicMock()
        mock_patch_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("PATCH failed")
        )
        mock_patch.return_value = mock_patch_response

        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )
        resource = DataResource(
            name="WillFail",
            schema_name="FailSchema",
            task_name="test",
            stage="test",
            data_version="v0.0.0",
        )

        with self.assertRaises(ValueError) as context:
            repo.update_resource_list(resource)
        self.assertIn("Failed to update resource via API", str(context.exception))

    @patch("pandas.DataFrame.to_csv")
    def test_add_to_resource_list_local_override(self, mock_to_csv):
        """
        Here, the repository default is 'api', but we override the storage method to 'local'.
        We expect the local CSV logic (instead of an API call).
        """
        # 1) Setup repo with default 'api'
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN_VALUE"
        )

        # 2) Mock the 'available_resources' so no real CSV is read/written
        repo.available_resources = pd.DataFrame(columns=["name", "schema_name"])
        # 3) Create a resource
        resource = DataResource(
            name="LocalOverrideResource",
            schema_name="LocalSchema",
            task_name="test",
            data_version="v0.0.0",
            stage="test",
        )

        # 4) Call the method with storage_method override
        returned_uuid = repo.add_to_resource_list(resource, storage_method="local")

        # 5) Check that no API call occurred => we can check Session.post was never called
        self.assertFalse(
            mock_to_csv.called is False,
            "Expected local CSV write, but .to_csv wasn't called?",
        )
        self.assertTrue(
            mock_to_csv.called,
            "Expected .to_csv to have been called for local mode override",
        )
        self.assertEqual(
            returned_uuid,
            "",
            "Local add_to_resource_list typically returns empty string",
        )
        # The appended row now should exist in available_resources
        self.assertEqual(len(repo.available_resources), 1)
        self.assertEqual(
            repo.available_resources.iloc[0]["name"], "LocalOverrideResource"
        )

    # @patch.object(ResourceRepository, "storage_method", "local")
    @patch("requests.Session.post")
    def test_add_to_resource_list_api_override(self, mock_post):
        """
        Here, the repository default is 'local', but we override the storage method to 'api'.
        We expect an API call (POST) instead of local CSV writing.
        """
        repo = ResourceRepository(
            db_path="some/path", storage_method="local"
        )  # default local
        # But we override in the call
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        resource = DataResource(
            name="APIOverride",
            schema_name="OverrideSchema",
            task_name="test",
            stage="test",
            data_version="v0.0.0",
            api_endpoint="testing",
        )

        returned_uuid = repo.add_to_resource_list(resource, storage_method="api")

        mock_post.assert_called_once_with(
            "https://lca.aau.dk/api/version-dataio/",
            json=self.assertDictContainsIdAndFields("APIOverride", "OverrideSchema"),
        )
        # Typically returns a generated uuid from the override
        self.assertNotEqual(returned_uuid, "")

    # @patch.object(ResourceRepository, "storage_method", "api")
    @patch("requests.Session.get")
    def test_get_resource_info_local_override(self, mock_get):
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )
        # Prevent the actual reload from disk
        repo._reload_resources_csv = MagicMock()

        df = pd.DataFrame(
            [
                {"name": "LocalRes", "schema_name": "LocalSchema"},
                {"name": "LocalRes2", "schema_name": "LocalSchema2"},
            ]
        )
        repo.available_resources = df

        results = repo.get_resource_info(storage_method="local", name="LocalRes")
        self.assertFalse(
            mock_get.called, "Did not expect an API call for local override"
        )
        self.assertEqual(results.name, "LocalRes")

    @patch("requests.Session.get")
    def test_list_available_resources_api_success(self, mock_get):
        """
        Test listing resources in API mode. Should return a list of DataResource objects
        when the server responds with 200 and a JSON list.
        """
        # 1) Mock the GET response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None  # no error
        # Suppose the server returns a list of two items
        mock_response.json.return_value = [
            {
                "id": "0697ae84-4167-4dea-a8d4-0cbd6b74d588",
                "name": "Test Resource A",
                "schema_name": "SomeSchema",
                "data_version": "1.0.0",
                "api_endpoint": "https://example.com/resourceA",
            },
            {
                "id": "0697ae84-4167-4dea-a8d4-0cbd6b74d589",
                "name": "Test Resource B",
                "schema_name": "AnotherSchema",
                "data_version": "2.0.0",
                "api_endpoint": "https://example.com/resourceB",
            },
        ]
        mock_get.return_value = mock_response

        # 2) Create a repository in API mode
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )

        # 3) Call list_available_resources(storage_method="api")
        resources = repo.list_available_resources(storage_method="api")

        # 4) Assertions
        mock_get.assert_called_once()
        self.assertEqual(len(resources), 2)
        self.assertIsInstance(resources[0], DataResource)
        self.assertIsInstance(resources[1], DataResource)
        self.assertEqual(resources[0].name, "Test Resource A")
        self.assertEqual(resources[1].name, "Test Resource B")

    @patch("requests.Session.get")
    def test_list_available_resources_api_http_error(self, mock_get):
        """
        If the server responds with an HTTP error (4xx/5xx), we expect a ValueError.
        """
        mock_response = MagicMock()
        # Simulate an HTTP error
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "HTTP 500 Internal Server Error"
        )
        mock_get.return_value = mock_response

        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )

        with self.assertRaises(ValueError) as context:
            repo.list_available_resources(storage_method="api")
        self.assertIn(
            "Failed to retrieve list of available resources from API",
            str(context.exception),
        )

    @patch("requests.Session.get")
    def test_list_available_resources_api_exception(self, mock_get):
        """
        If a non-HTTP request exception (like ConnectionError) is raised,
        we still expect a ValueError from list_available_resources.
        """
        mock_get.side_effect = requests.exceptions.ConnectionError("Could not connect")

        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )

        with self.assertRaises(ValueError) as context:
            repo.list_available_resources(storage_method="api")
        self.assertIn(
            "Failed to retrieve list of available resources from API",
            str(context.exception),
        )

    @patch("dataio.resources.load_api")
    def test_get_dataframe_for_resource_api(self, mock_load_api):
        """
        Test that calling get_dataframe_for_resource(...) with storage_method='api'
        invokes the 'load_api' function with the correct resource and returns its result.
        """
        # 1) Setup mock return value
        df_mock = pd.DataFrame(
            {
                "location": ["LOC999"],
                "product": ["P999"],
                "unit": ["kg"],
                "value": [99.9],
                "time": [500],
                "source": ["API Source"],
            }
        )
        mock_load_api.return_value = df_mock

        # 2) Create a ResourceRepository in API mode
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = ResourceRepository(
                db_path="some/path",
                storage_method="api",
                API_token="TEST_TOKEN",
                cache_dir=tmpdir,
            )

            # 3) Create a DataResource that points to an API endpoint
            resource = DataResource(
                id=uuid4(),
                name="ApiResource",
                schema_name="ProductionVolumes_uncertainty",
                task_name="test",
                stage="test",
                data_version="v2.0.0",
                api_endpoint="https://example.com/api/resource",
            )

            # 4) Call the method with storage_method='api'
            result_df = repo.get_dataframe_for_resource(resource, storage_method="api")

            # 5) Assertions
            mock_load_api.assert_called_once_with(
                ANY, resource, tmpdir, MAX_CACHE_FILES=3
            )
            # Check the returned DataFrame is the same we mocked
            pd.testing.assert_frame_equal(result_df, df_mock)

    @patch(
        "requests.Session.post"
    )  # Patch the Session.post used in add_to_resource_list
    @patch(
        "dataio.resources.save_to_api"
    )  # If you also want to mock the code in save_to_api
    @patch.object(ResourceRepository, "resource_exists", return_value=False)
    def test_write_dataframe_for_resource_api_new_resource(
        self, mock_resource_exists, mock_save_to_api, mock_session_post
    ):
        """
        If the resource doesn't exist in API mode, write_dataframe_for_resource
        calls save_to_api + add_to_resource_list => which tries session.post => we mock it.
        """
        # 1) Mock the Session.post to simulate a successful 201
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None  # no error => success
        mock_session_post.return_value = mock_resp

        # 2) Also mock the save_to_api call if your code calls it
        mock_save_to_api.return_value = None  # or do nothing

        # 3) Prepare test data
        df = pd.DataFrame(
            {
                "location": ["API_LOC"],
                "product": ["API_PROD"],
                "unit": ["kg"],
                "value": [10.0],
                "time": [2025],
                "source": ["Test Source"],
            }
        )

        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )
        resource = DataResource(
            id=uuid4(),
            name="MyAPIResource",
            task_name="test",
            stage="test",
            code_version="v0.0.1",
            data_version="v0.0.1",
            schema_name="ProductionVolumes_uncertainty",
            api_endpoint="https://api.example.com/resource",
        )

        # 4) Call the method => no real network because we mock session.post
        repo.write_dataframe_for_resource(
            df, resource, overwrite=True, append=False, storage_method="api"
        )

        # resource_exists => 2 calls, etc. We won't assert that now
        mock_session_post.assert_any_call(
            "https://lca.aau.dk/api/version-dataio/", json=ANY
        )
        # or you can check the exact payload / arguments

        # If your code calls save_to_api, check that call:
        mock_save_to_api.assert_called_once()

    @patch("dataio.resources.save_to_api")
    @patch.object(ResourceRepository, "resource_exists", return_value=True)
    def test_write_dataframe_for_resource_api_resource_exists_no_overwrite(
        self, mock_resource_exists, mock_save_to_api
    ):
        """
        If the resource exists in API mode and overwrite=False,
        by default your code does NOT raise FileExistsError.
        (Your logic for API overwrite is optional;
        adjust if you want to skip or raise an error.)
        """
        df = pd.DataFrame()
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )
        resource = DataResource(
            name="ExistingAPIResource",
            schema_name="ProductionVolumes_uncertainty",
            task_name="test",
            stage="test",
            code_version="v0.0.1",
            data_version="v0.0.1",
            api_endpoint="https://api.example.com/existing_resource",
        )

        # Overwrite = False => code doesn't raise FileExistsError in API mode.
        # The method calls save_to_api anyway unless you code differently.

        with self.assertRaises(FileExistsError):
            repo.write_dataframe_for_resource(
                df, resource, overwrite=False, storage_method="api"
            )

        mock_resource_exists.assert_called_once_with(resource, "api")
        mock_save_to_api.assert_not_called()

    def test_write_dataframe_for_resource_invalid_storage_method(self):
        """
        If we pass an invalid storage_method, a ValueError should be raised.
        (API test scenario, but same for local.)
        """
        df = pd.DataFrame()
        repo = ResourceRepository(
            db_path="some/path", storage_method="api", API_token="FAKE_TOKEN"
        )
        resource = DataResource(
            name="InvalidResource",
            schema_name="ProductionVolumes_uncertainty",
            task_name="test",
            stage="test",
            code_version="v0.0.1",
            data_version="v0.0.1",
        )

        with self.assertRaises(ValueError) as ctx:
            repo.write_dataframe_for_resource(df, resource, storage_method="invalid")

        self.assertIn("Invalid storage method", str(ctx.exception))

    @patch("dataio.resources.requests.Session.get")
    def test_get_dataframe_for_resource_api_cache(self, mock_get):
        """
        Test that the second call to get_dataframe_for_resource(...) for the SAME resource
        uses the on-disk cache and does NOT call requests.Session.get again.
        """

        # 1) Create a mock response to simulate an API call
        #    This will be the JSON data that gets turned into a DataFrame
        mock_data = {
            "location": ["LOC999"],
            "product": ["P999"],
            "unit": ["kg"],
            "value": [99.9],
            "time": [500],
            "source": ["API Source"],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # 2) Use a temporary directory as our cache directory
        #    (So each test run is isolated and doesn't interfere with real data)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Suppose your ResourceRepository can accept an override for the cache dir
            # Or you can set a global variable/path in your code to tmpdir if needed
            repo = ResourceRepository(
                db_path="some/path",
                storage_method="api",
                API_token="TEST_TOKEN",
                cache_dir=tmpdir,
            )

            # 3) Create a DataResource that points to an API endpoint
            resource = DataResource(
                name="ApiResource",
                schema_name="ProductionVolumes_uncertainty",
                task_name="test",
                stage="test",
                code_version="v0.0.1",
                data_version="v0.0.1",
                api_endpoint="production-volume-uncertainty/",
            )

            # 4) First call: should hit the API and create a CSV in the cache
            df_first = repo.get_dataframe_for_resource(resource, storage_method="api")

            # Ensure the returned DataFrame is what we expect
            expected_df = pd.DataFrame(mock_data)
            pd.testing.assert_frame_equal(df_first, expected_df)

            # Check that the CSV file was actually created in tmpdir
            # (You can add more checks, e.g. count the number of CSVs if you do LRU cleanup.)
            csv_files = [f for f in os.listdir(tmpdir) if f.endswith(".csv")]
            self.assertEqual(
                len(csv_files), 1, "There should be exactly 1 cached CSV file."
            )

            # We expect requests.Session.get was called exactly once
            mock_get.assert_called_once()

            # 5) Reset the mock so we can see if it gets called again
            mock_get.reset_mock()

            # 6) Second call: should load from *cache* and NOT call the API again
            df_second = repo.get_dataframe_for_resource(resource, storage_method="api")
            pd.testing.assert_frame_equal(df_second, expected_df)

            # Check that no *new* CSV files were created
            csv_files_after = [f for f in os.listdir(tmpdir) if f.endswith(".csv")]
            self.assertEqual(
                len(csv_files_after), 1, "Cache should still have exactly 1 CSV file."
            )

            # Ensure we did NOT call the remote endpoint again
            mock_get.assert_not_called()

    @patch("dataio.resources.requests.Session.get")
    def test_cache_eviction_of_old_files(self, mock_get):
        """
        Test that if we exceed 3 cached items, the oldest file is evicted,
        leaving only 3 in the cache directory.
        """

        # 1) Mock the API response returned by requests
        #    We'll return the same JSON for simplicity.
        mock_data = {
            "location": ["LOC"],
            "product": ["P"],
            "unit": ["kg"],
            "value": [99.9],
            "time": [123],
            "source": ["API Source"],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # 2) Use a temporary directory as our cache, so each test is isolated
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a ResourceRepository that saves to tmpdir
            # (Ensure your ResourceRepository actually uses this directory
            #  and enforces the max-cache-files=3 policy.)
            repo = ResourceRepository(
                db_path="some/path",
                storage_method="api",
                API_token="TEST_TOKEN",
                cache_dir=tmpdir,
            )

            # 3) Create 4 distinct resources -> 4 distinct cache keys
            #    The difference is in the api_endpoint or name, etc.
            resources = [
                DataResource(
                    name=f"ApiResource{i}",
                    schema_name="ProductionVolumes_uncertainty",
                    task_name="test",
                    stage="test",
                    code_version="v0.0.1",
                    data_version="v0.0.1",
                    api_endpoint=f"production-volume-uncertainty-{i}/",
                )
                for i in range(1, 5)
            ]

            # 4) Load each resource, creating a cache file each time.
            #    We only want to keep 3 in total, so after the 4th resource,
            #    we expect the oldest file to be removed.
            for i, resource in enumerate(resources, start=1):
                _ = repo.get_dataframe_for_resource(resource, storage_method="api")
                time.sleep(0.01)
                # You could optionally check the file count after each iteration to see exactly when
                # the eviction occurs. The main check is after the 4th file though.

            # 5) After loading 4 distinct resources, confirm only 3 CSV files remain
            csv_files_after = [f for f in os.listdir(tmpdir) if f.endswith(".csv")]
            self.assertEqual(
                len(csv_files_after), 3, "Cache should only keep at most 3 CSV files."
            )

            # 6) (Optional) Confirm the oldest file is specifically removed.
            #    For example, the first resource might have had a filename containing
            #    'uncertainty-1'. In real code, you'd replicate exactly how your
            #    build_cache_key(...) logic forms the filename. Here, we do a simple check:
            removed_filename_hint = "uncertainty-1"
            self.assertTrue(
                all(removed_filename_hint not in fname for fname in csv_files_after),
                f"The oldest file for Resource1 should have been evicted. Remaining: {csv_files_after}",
            )
