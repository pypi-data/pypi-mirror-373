from io import StringIO

import pytest
import yaml

from dataio.load import load_metadata


# Function to simulate reading from file
def mock_open(mock=None):
    if mock is None:
        mock = StringIO(
            """
  - id: '123e4567-e89b-12d3-a456-426614174000'
    created_by:
        email: 'user@example.com'
        name: 'John Doe'
    last_modified: 2021-06-01T13:00:00
    license:
        name: 'CC BY-SA'
        description: 'Creative Commons License'
        url: 'https://creativecommons.org/licenses/by-sa/4.0/'
        create_time: 2021-06-01T12:00:00
    version:
        version: '1.0'
        create_time: 2021-06-01T12:00:00
        comments: 'Initial release'
        """
        )
    return mock


@pytest.fixture
def mock_file(monkeypatch):
    monkeypatch.setattr("builtins.open", lambda file, mode: mock_open())


def test_load_metadata_from_yaml(mock_file):
    result = load_metadata("dummy_path.yaml")
    assert isinstance(result, dict)
    assert "123e4567-e89b-12d3-a456-426614174000" in result
    metadata = result["123e4567-e89b-12d3-a456-426614174000"]
    assert metadata.created_by.email == "user@example.com"
    assert metadata.license.name == "CC BY-SA"
