from logging import getLogger
from pathlib import Path

import pytest
import yaml

from dataio.config import Config

logger = getLogger("unit_test")


def test_load_config_from_yaml() -> None:
    config = Config("current_task_name")
    assert config.fao_cfile == "20230404", "error in global file"
    assert config.pasture == [
        "Land under perm. meadows and pastures",
        "Land under temp. meadows and pastures",
        "Permanent meadows and pastures",
        "Temporary meadows and pastures",
    ], "error in data file"
    assert config.retailer_sec["Retailer"] == [
        "A_TDRT",
        "A_TDWH",
    ], "error in data file subdivision"
    return None


def test_load_config_from_localfile() -> None:
    """Test import of a config file from local computer"""
    config_file_path = Path(__file__).parent / "test" / "global.config.test.yaml"
    task_name = "current_task_name"
    fao_cfile_value = "aaaaaaa"

    config = Config(task_name, config_path=config_file_path)
    assert (
        config.fao_cfile == fao_cfile_value
    ), "error in global file"  # add the key 'fao_cfile' and the value you want to test
    return None
