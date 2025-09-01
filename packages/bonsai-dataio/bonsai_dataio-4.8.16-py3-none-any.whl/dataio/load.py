"""Datapackage load module of dataio utility."""

import ast
import glob
import hashlib
import json
import os
import re
import warnings
from io import StringIO
from logging import getLogger
from pathlib import Path
from typing import Dict

import h5py
import pandas as pd
import requests
import yaml
from pydantic import BaseModel

import dataio.schemas.bonsai_api as schemas
from dataio.save import (
    SUPPORTED_DICT_FILE_EXTENSIONS,
    SUPPORTED_MATRIX_FILE_EXTENSIONS,
    SUPPORTED_TABLE_FILE_EXTENSIONS,
)
from dataio.schemas.bonsai_api import DataResource
from dataio.schemas.bonsai_api.base_models import MatrixModel
from dataio.tools import BonsaiBaseModel
from dataio.validate import validate_matrix, validate_table

from .set_logger import set_logger

logger = getLogger("root")

accepted_na_values = ["", "NaN", "N/A", "n/a", "nan"]


def load_metadata(path_to_metadata, datapackage_names=None):
    """
    Load metadata from a YAML file and convert it into a dictionary with UUIDs as keys and MetaData objects as values.
    The YAML file is expected to start directly with a list of metadata entries.

    Parameters
    ----------
    file_path : str
        The path to the YAML file that contains metadata entries.

    Returns
    -------
    dict
        A dictionary where each key is a UUID (as a string) of a MetaData object and each value is the corresponding MetaData object.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    yaml.YAMLError
        If there is an error in parsing the YAML file.
    pydantic.ValidationError
        If an item in the YAML file does not conform to the MetaData model.

    Examples
    --------
    Assuming a YAML file located at 'example.yaml':

    >>> metadata_dict = load_metadata_from_yaml('example.yaml')
    >>> print(metadata_dict['123e4567-e89b-12d3-a456-426614174000'])
    MetaData(id=UUID('123e4567-e89b-12d3-a456-426614174000'), created_by=User(...), ...)
    """
    logger.info(f"Started loading metadata from {path_to_metadata}")

    if datapackage_names:
        # TODO load from API
        pass
    else:
        metadata = load_dict_file(path_to_metadata, schemas.MetaData)
        logger.info("Finished loading metadata")
    return metadata


def load_dict_file(path_to_file, schema: BaseModel):
    result_dict = {}
    try:
        with open(path_to_file, "r") as file:
            data = yaml.safe_load(file)

        for item in data:
            result_obj = schema(**item)
            result_dict[str(result_obj.id)] = result_obj

    except FileNotFoundError:
        logger.error(
            "Could not open dataio datapackage metadata file " f"{path_to_file}."
        )
        raise

    return result_dict


def load_table_file(path_to_file: Path, schema: BonsaiBaseModel, **kwargs):
    str_path = str(path_to_file)
    if str_path.endswith(".pkl"):
        df = pd.read_pickle(path_to_file, **kwargs)
    elif str_path.endswith(".csv"):
        df = pd.read_csv(
            path_to_file,
            dtype=schema.get_csv_field_dtypes(),
            keep_default_na=False,
            na_values=accepted_na_values,
        )
        if not df.empty and "samples" in df.columns:
            # Ensure that the 'samples' column is read correctly by replacing spaces between numbers with commas,
            # and fixing the formatting of brackets to match the expected list format.
            pattern = re.compile(r"(?<=\d)\s+(?=\d)")
            # Apply the pattern to each string in the list
            df["samples"] = [
                pattern.sub(", ", s).replace("[ ", "[").replace(" ]", "]")
                for s in df["samples"]
            ]
            df["samples"] = df["samples"].apply(ast.literal_eval)

        for col_name, type in schema.get_csv_field_dtypes().items():
            if col_name in df.columns and type == "str":
                df[col_name] = df[col_name].fillna("")
    elif ".xls" in str_path:
        df = pd.read_excel(path_to_file, **kwargs)
    elif str_path.endswith(".parquet"):
        df = pd.read_parquet(path_to_file, **kwargs)
    else:
        raise ValueError(f"Failed to import {str_path}")

    validate_table(df, schema)

    return df


def load_matrix_file(path_to_file: Path, schema: MatrixModel, **kwargs):
    df = pd.read_hdf(path_to_file, **kwargs)
    validate_matrix(df, schema)

    return df


def load(path: Path, schemas: Dict[str, BaseModel] = None):
    """
    This will return an empty dict if the file can't be found
    """

    loaded_files = {}

    if path.name.startswith("http"):
        # if path is a url, connect to the API url and load the package names
        # defined in the keys of the schemas dict
        df = self._read_http(*args, **kwargs)

    elif path.exists():
        if path.is_dir():
            # If path is a directory, read all files in the directory
            for file in path.iterdir():
                # If path is a file, just load the file
                if file.suffix in SUPPORTED_DICT_FILE_EXTENSIONS:
                    loaded_files[file.stem] = load_dict_file(file, schemas[file.stem])
                # If path is a file, just load the file
                elif file.suffix in SUPPORTED_TABLE_FILE_EXTENSIONS:
                    loaded_files[file.stem] = load_table_file(file, schemas[file.stem])
                elif path.suffix in SUPPORTED_MATRIX_FILE_EXTENSIONS:
                    loaded_files[path.stem] = load_matrix_file(path, schemas[path.stem])

        else:
            # If path is a file, just load the file
            if path.suffix in SUPPORTED_DICT_FILE_EXTENSIONS:
                loaded_files[path.stem] = load_dict_file(path, schemas[path.stem])
            # If path is a file, just load the file
            elif path.suffix in SUPPORTED_TABLE_FILE_EXTENSIONS:
                loaded_files[path.stem] = load_table_file(path, schemas[path.stem])
            elif path.suffix in SUPPORTED_MATRIX_FILE_EXTENSIONS:
                loaded_files[path.stem] = load_matrix_file(path, schemas[path.stem])

    if len(loaded_files) == 1:
        return next(iter(loaded_files.values()))
    return loaded_files


def build_cache_key(resource: DataResource) -> str:
    """
    Builds a unique string key for caching based on:
      - resource.api_endpoint
      - relevant fields (version, task_name, etc.)
    """
    # Gather the query-relevant fields in a dict
    # (Adjust to match the query params you actually pass.)
    query_params = {
        "api_endpoint": resource.api_endpoint or "",
        "version": str(resource.id) if resource.id else "",
        "task_name": resource.task_name or "",
        "stage": resource.stage or "",
        "name": resource.name or "",
        "data_version": resource.data_version or "",
        "dag_run_id": resource.dag_run_id or "",
    }

    # Convert the dict to a canonical JSON string so it's stable
    # Then hash it to get a short-ish cache key
    as_json = json.dumps(query_params, sort_keys=True)
    hash_str = hashlib.md5(as_json.encode("utf-8")).hexdigest()

    # You can return just the hash, or "endpoint_hash", or embed fields in your key
    # For clarity, let's prefix with the endpoint so it's easy to see from filename
    # (just be mindful that some endpoints might contain characters not ideal for filenames)
    # We'll do a sanitized endpoint, e.g. replace slashes with underscores:
    safe_endpoint = (resource.api_endpoint or "").replace("/", "_")

    # final key
    return f"{safe_endpoint[:50]}_{hash_str}"


def get_cache_path(key: str, CACHE_DIR="./data_cache/") -> str:
    """
    Returns a local file path where the DataFrame is cached,
    based on the unique cache key.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    # We'll store everything as csv, for instance:
    return os.path.join(CACHE_DIR, f"{key}.csv")


def clean_up_cache(CACHE_DIR, MAX_CACHE_FILES):
    """
    Enforce that only up to MAX_CACHE_FILES CSV files remain in CACHE_DIR.
    Remove the oldest files (by modification time) if there are more than that.
    """
    csv_files = glob.glob(os.path.join(CACHE_DIR, "*.csv"))
    if len(csv_files) <= MAX_CACHE_FILES:
        return  # Nothing to do

    # Sort by modification time, oldest first
    csv_files.sort(key=os.path.getmtime)

    # Number of files over the limit
    num_to_remove = len(csv_files) - MAX_CACHE_FILES
    for i in range(num_to_remove):
        os.remove(csv_files[i])


def load_api(self, resource: DataResource, CACHE_DIR, MAX_CACHE_FILES) -> pd.DataFrame:
    """
    Fetches data from the resource's API endpoint and returns it as a DataFrame.
    Assumes the endpoint returns CSV text (adjust as needed for JSON, etc.).

    Raises
    ------
    ValueError
        If api_endpoint is not set or an HTTP error occurs.
    """
    if not resource.api_endpoint:
        raise ValueError(
            f"Resource '{resource.name}' has no 'api_endpoint' but is expected "
            "to be loaded via API. Cannot fetch remote data."
        )
    # Build a unique cache key based on resource fields
    cache_key = build_cache_key(resource)
    cache_path = get_cache_path(cache_key, CACHE_DIR)

    # 1) If cached file exists, load and return immediately
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)

    # If not in memory or disk, fetch from remote
    # Build a dictionary of possible parameters from fields on the resource.
    # Adjust the field names to match your actual DataResource attributes.
    params = {}

    # If the resource has a known version/id (often a UUID),
    # pass it under the "version" param (this is how your DRF endpoint expects it).
    if getattr(resource, "id", None):
        params["version"] = str(resource.id)

    # Pull in any of the other fields you want:
    if getattr(resource, "task_name", None):
        params["task_name"] = resource.task_name

    if getattr(resource, "stage", None):
        params["stage"] = resource.stage

    if getattr(resource, "name", None):
        params["name"] = resource.name

    if getattr(resource, "data_version", None):
        params["data_version"] = resource.data_version

    if getattr(resource, "dag_run_id", None):
        params["dag_run_id"] = resource.dag_run_id

    try:
        response = self.session.get(resource.api_endpoint, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(
            f"Failed to fetch data from API endpoint '{resource.api_endpoint}': {e}"
        )

    # Convert response JSON -> DataFrame
    data = response.json()
    df = pd.DataFrame(data)

    # 3) Save to CSV
    df.to_csv(cache_path, index=False)

    # 4) Clean up old files in our cache if we exceed MAX_CACHE_FILES
    clean_up_cache(CACHE_DIR, MAX_CACHE_FILES)

    return df
