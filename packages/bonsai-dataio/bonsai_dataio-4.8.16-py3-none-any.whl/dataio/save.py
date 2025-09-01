"""Datapackage save module of dataio utility."""

import json
import logging
import os
from io import StringIO
from logging import getLogger
from pathlib import Path
from uuid import uuid4

import h5py
import numpy as np
import pandas as pd
import requests
import yaml

from dataio.schemas.bonsai_api import DataResource
from dataio.tools import BonsaiBaseModel, BonsaiTableModel
from dataio.validate import validate_matrix, validate_table

from .set_logger import set_logger

logger = getLogger("root")

SUPPORTED_TABLE_FILE_EXTENSIONS = [".parquet", ".xlsx", ".xls", ".csv", ".pkl"]

SUPPORTED_DICT_FILE_EXTENSIONS = [".json", ".yaml"]

SUPPORTED_MATRIX_FILE_EXTENSIONS = [".hdf5", ".h5"]


def save_dict(data, path: Path, append=False):

    if isinstance(data, BonsaiBaseModel):
        data_dict = data.model_dump()
    elif isinstance(data, dict):
        data_dict = data
    else:
        assert False, "Data format not supported, use dict or BonsaiBaseModel"
    write_type = "w"
    if append:
        write_type = "w+"

    if path.suffix == ".yaml":
        with open(path, write_type) as file:
            yaml.dump(data_dict, file)
    elif path.suffix == ".json":
        with open(path, write_type) as file:
            json.dump(data_dict, file)


def save_table(data, path: Path, append=False):

    if isinstance(data, BonsaiTableModel):
        df = data.to_pandas()
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        assert False, "Data format not supported, use DataFrame or BonsaiTableModel"

    mode = "w"
    if append:
        mode = "a"

    skip_header = not (path.exists() and append)

    if path.suffix == ".parquet":
        if append:
            logger.error("Append is not supported for .parquet files")
        else:
            df.to_parquet(path)
    elif path.suffix == ".xlsx" or path.suffix == ".xls":
        with pd.ExcelWriter(path, mode=mode) as writer:
            df.to_excel(writer, header=skip_header)
    elif path.suffix == ".csv":
        df.to_csv(
            path,
            mode=mode,
            index=False,
            date_format="%Y-%m-%d %H:%M:%SZ",
            header=skip_header,
        )
    elif path.suffix == ".pkl":
        if append:
            logger.error("Append is not supported for .pkl files")
        else:
            df.to_pickle(path)


def save_matrix(data: pd.DataFrame, name: str, path: Path, append=False):
    # Function to save DataFrame to HDF5 file with index and columns

    mode = "w"
    if append:
        mode = "a"
    data.to_hdf(path, key=name, mode=mode)


def save(data, name: str, path: Path, schema=None, overwrite=True, append=False):

    loaded_files = {}

    if not schema:
        return old_save(data, path)

    if path.name.startswith("http"):
        # if path is a url, connect to the API url and load the package names
        # defined in the keys of the schemas dict
        df = self._read_http(*args, **kwargs)

    else:
        if not path.parent.exists():
            path.parent.mkdir(parents=True)

        if path.exists() and not overwrite and append:
            # If path is a file, just load the file
            if path.suffix in SUPPORTED_DICT_FILE_EXTENSIONS:
                save_dict(data, path, True)
            # If path is a file, just load the file
            elif path.suffix in SUPPORTED_TABLE_FILE_EXTENSIONS:
                # validate data before it is written
                validate_table(data, schema=schema)
                save_table(data, path, True)
            elif path.suffix in SUPPORTED_MATRIX_FILE_EXTENSIONS:
                validate_matrix(data, schema=schema)
                save_matrix(data, name, path, True)
        else:
            # If path is a file, just load the file
            if path.suffix in SUPPORTED_DICT_FILE_EXTENSIONS:
                save_dict(data, path, False)
            # If path is a file, just load the file
            elif path.suffix in SUPPORTED_TABLE_FILE_EXTENSIONS:
                # validate data before it is written
                validate_table(data, schema=schema)
                save_table(data, path, False)
            elif path.suffix in SUPPORTED_MATRIX_FILE_EXTENSIONS:
                validate_matrix(data, schema=schema)
                save_matrix(data, name, path)


def old_save(
    datapackage,
    root_path: str = ".",
    increment: str = None,
    overwrite: bool = False,
    create_path: bool = False,
    log_name: str = None,
):
    """Save datapackage from dataio.yaml file.

    Parameters
    ----------
    datapackage: DataPackage
      dataio datapackage
    root_path : str
      path to root of database
    increment : str
      semantic level to increment, in [None, 'patch', 'minor', 'major']
    overwrite : bool
      whether to overwrite
    create_path : bool
      whether to create path
    log_name : str
      name of log file, if None no log is set
    """
    logger.info("Started datapackage save")

    metadata = datapackage.__metadata__
    full_path = Path(root_path).joinpath(metadata["path"])

    # open log file
    if log_name is not None:
        set_logger(filename=log_name, path=full_path.parent, overwrite=overwrite)
        logger.info("Started dataio plot log file")
    else:
        logger.info("Not initialized new log file")

    # Auto-increment
    if increment is None:
        logger.info("No version number auto-increment")
    else:
        logger.info("Attempting to auto-increment version number")
        if "version" not in metadata.keys():
            logger.warning("No version field in metadata, so no increment")
        else:
            try:
                version_list = version_str2list(metadata["version"])
            except ValueError:
                logger.warning(
                    "Metadata version is not in semantic format, "
                    f"so no auto-increment: {metadata['version']}"
                )
            semantic_level_list = ["patch", "minor", "major"]
            semantic_level_pos = [2, 1, 0]
            if increment in semantic_level_list:
                pos = semantic_level_list.index(increment)
                version_list[semantic_level_pos[pos]] += 1
                version_str = version_list2str(version_list)
                metadata["version"] = version_str
                logger.info(
                    f"Given semantic_level '{increment}', the "
                    f"new version number is '{version_str}'"
                )
            else:
                logger.warning(
                    "Unrecogninzed semantic level, no increment: "
                    f"{increment}. Should be in ['patch', "
                    "'minor', 'major']"
                )

    # check path exists and overwrite options
    if not os.path.exists(full_path):
        if create_path:
            os.makedirs(full_path)
            logger.info(f"Path {full_path} created")
        else:
            logger.error(
                f"Path {full_path} does not exist and 'create_path' "
                "option is disabled"
            )
            raise FileNotFoundError
    if len(os.listdir(full_path)) > 0:
        if not overwrite:
            logger.error(
                f"Path {full_path} is not empty and 'overwrite' " "option is disabled"
            )
            raise FileExistsError

    # export csvs
    for pos, table in enumerate(metadata["tables"]):
        delimiter = ","
        quotechar = '"'
        if "dialect" in table.keys():
            if "csv" in table["dialect"].keys():
                if "delimiter" in table["dialect"]["csv"].keys():
                    delimiter = table["dialect"]["csv"]["delimiter"]
                if "quoteChar" in table["dialect"]["csv"].keys():
                    quotechar = table["dialect"]["csv"]["quoteChar"]
                if "skipInitialSpace" in table["dialect"]["csv"].keys():
                    if table["dialect"]["csv"]["skipInitialSpace"]:
                        logger.warning(
                            f"Initial space skip in table {table['name']} metadata "
                            "originally True and set to False"
                        )
                        table["dialect"]["csv"]["skipInitialSpace"] = False
                        metadata["tables"][pos] = table

        csv_path = full_path.joinpath(table["path"])
        df = datapackage.__dict__[table["name"]]
        df["id"] = df.index
        df.insert(0, "id", df.pop("id"))
        df.to_csv(csv_path, index=False, sep=delimiter, quotechar=quotechar)
        logger.info(f"Exported table {table['name']} to {csv_path}")

    # export metadata
    meta_path = full_path.joinpath(f"{metadata['name']}.dataio.yaml")
    try:
        with open(meta_path, "w") as f:
            yaml.safe_dump(metadata, f)
    except FileNotFoundError:
        logger.error(f"File '{meta_path}' could not be " "exported to output path")
    logger.info(f"Exported metadata to {meta_path}")

    logger.info("Finished datapackage save")


def version_str2list(version_str):
    """Convert semantic version string 'vMAJOR.MINOR.PATCH' to list."""
    version_list = version_str.split(".")
    version_list[0] = version_list[0][1:]
    version_list = [int(version_level) for version_level in version_list]
    return version_list


def version_list2str(version_list):
    """Convert semantic version list to string 'vMAJOR.MINOR.PATCH'."""
    str_level = [str(version_level) for version_level in version_list]
    version_str = ".".join(str_level)
    return "v" + version_str


def save_to_api(
    data: pd.DataFrame,
    resource: DataResource,
    schema=None,
    overwrite=True,
    append=False,
):
    """
    Saves the given DataFrame to resource.api_endpoint via a single JSON POST.
    The JSON body has the form:
      {
        "data": [
           {...},
           {...}
        ]
      }

    so that multiple rows can be created in one request (per your test example).

    Parameters
    ----------
    data : pd.DataFrame
        The data to be sent. Each row becomes one dict.
    resource : DataResource
        Must have a non-empty 'api_endpoint'.
        (Optionally add resource.id => references the 'version' if your endpoint requires it.)
    schema : optional
        If you want to validate 'data' before sending, do so here.
    overwrite : bool
        If your API supports 'overwrite', pass it as a query param or in the body
        (depending on your API).

    Raises
    ------
    ValueError
        If 'resource.api_endpoint' is missing or if the POST fails.
    """

    if not resource.api_endpoint:
        raise ValueError(
            f"Resource '{resource.name}' has no api_endpoint. Cannot save via API."
        )

    # assign the resource id to version
    data["version"] = resource.id

    payload = data.to_dict(orient="records")

    # Overwrite logic: e.g., pass as query params
    params = {
        "overwrite": "true" if overwrite else "false",
        "append": "true" if append else "false",
    }

    try:
        response = requests.post(resource.api_endpoint, json=payload, params=params)
        response.raise_for_status()  # Raises HTTPError if 4XX or 5XX
    except requests.RequestException as exc:
        raise ValueError(
            f"Failed to save data to API endpoint '{resource.api_endpoint}': {exc}"
        )
