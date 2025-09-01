"""This is an utility module to store data into the group folder of BONSAI project
Created on Jul 15, 2022

@author: Fan Yang

Todo:


"""

import logging
import pickle
from collections import namedtuple
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List

import frictionless
import pandas as pd
import yaml
from data_io.dataclasses import (
    Algorithm,
    AttributeTable,
    Author,
    DataPackage,
    FactTable,
    License,
    ModifiedBy,
    Source,
)
from frictionless import Package, Resource, describe, extract, validate
from yaml.loader import FullLoader

# self.level = level
# self.logger = logging.getLogger("data_io")
# self.logger.setLevel(level)
# self.logger.addHandler(handler)


def _version_to_path(version_string: str):
    """
    Converts a version string into a pathlib.Path instance.

    Version string needs to be in the format MAJOR.MINOR.PATCH.

    Parameters
    ----------
    version_string : str
        The version string to convert to a Path instance.

    Returns
    -------
    pathlib.Path
        The corresponding pathlib.Path instance.
    """
    versions = version_string.split(".")

    if len(versions) == 2:
        [major, minor] = versions
        return Path(major) / minor

    if len(versions) == 3:
        [major, minor, patch] = versions
        return Path(major) / minor / patch

    raise ValueError(
        f"Malformated version string {version_string}, should be either MAJOR.MINOR.PATCH or MAJOR.MINOR."
    )


def _category_path_to_path(category_path: str):
    """
    Converts a category ID string into a pathlib.Path instance.

    Category ID needs to be in the format SOME/CATEGORY/STACK.

    Parameters
    ----------
    category_path : str
        The category ID string to convert to a Path instance.

    Returns
    -------
    pathlib.Path
        The corresponding pathlib.Path instance.
    """
    error = ValueError(
        f"Invalid category_path {category_path}, should have format SOME/CATEGORY/STACK."
    )

    if "\\" in category_path:
        raise error

    values = category_path.split("/")

    path = Path(values[0])
    for item in values[1:]:
        if not item:
            raise error
        path = path / item
    return path


def write(param_dict, datapackage: DataPackage, perform_checks=True):
    """
    Writes the given DataPackage instance to the file system, performing optional integrity checks.
    The method will create the necessary directories based on the root_path, category_path, and version.
    The DataPackage's tables are written as CSV files, and the metadata is written as a YAML file.
    The output files adhere to the frictionless format, adding some additional metadata.

    Parameters
    ----------
    param_dict : dict
        A dictionary containing the root_path and other parameters. The root_path is used as the base
        directory to store the DataPackage.
    datapackage : DataPackage
        The DataPackage instance to write to the file system.
    perform_checks : bool, optional
        If True (default), performs integrity checks on the DataPackage instance before writing it.
        The checks ensure that the DataPackage has a name, source, modified_by, and target_language.
    """

    datapackage.assert_completeness()

    # TODO: look for non-standard metadata entries and use them to create additional columns
    # TODO:

    if "root_path" in param_dict:
        path = Path(param_dict["root_path"])
        path = (
            path
            / _category_path_to_path(datapackage.category_path)
            / datapackage.name
            / _version_to_path(datapackage.version)
        )

        if not path.exists():
            path.mkdir(parents=True)

        resources = []
        for name, table in datapackage.tables.items():
            file_path = path / f"{name}.csv"
            table.to_csv(file_path)
            resource = frictionless.describe(table.data, name=name)
            resource.data = None
            resource.path = f"{name}.csv"
            resource.scheme = None
            resource.format = "csv"
            resource.mediatype = None
            metadata = resource.metadata_export()
            metadata.update({"tabletype": table.type})

            if isinstance(table, AttributeTable):
                metadata.update(
                    {"attribute_name": table.name, "attribute_category": table.category}
                )

            resource = resource.metadata_import(metadata)
            for index_name in table.data.index.names:
                f = table.fields[index_name]
                if f.foreign_name:
                    foreign_key = {
                        "fields": [index_name],
                        "reference": {
                            "resource": f.resource,
                            "fields": [f.foreign_name],
                        },
                    }
                    if f.external_path:
                        foreign_key["reference"].update(
                            {"external_path": f.external_path}
                        )
                    resource.schema.foreign_keys.append(foreign_key)
            resources.append(resource)

        package = Package(resources=resources)

        source = datapackage.source.__dict__.copy()
        license = source.pop("license")

        authors = [author.__dict__ for author in datapackage.modified_by.authors]

        package = package.metadata_import(
            {
                "name": datapackage.name,
                "category_path": datapackage.category_path,
                "title": datapackage.title,
                "comment": datapackage.comment,
                "version": datapackage.version,
                "last_modified": datapackage.last_modified,
                "modified_by": {
                    "algorithm": datapackage.modified_by.algorithm.__dict__,
                    "authors": authors,
                },
                "license": license.__dict__,
                "source": source,
                "resources": package.resources,
                "target_language": datapackage.target_language,
                "encoding": datapackage.encoding,
            }
        )

        dict = package.to_dict()
        with open(path / f"{datapackage.name}.datapackage.yaml", "w") as file:
            yaml.dump(dict, file)


def read(param_dict: Dict, perform_checks=True):
    """
    Reads a DataPackage from the file system using the provided parameters. By default, it tries to
    load a frictionless data package using a descriptor YAML file. The method reads the metadata
    and the data tables (CSV files) from the specified path.

    Parameters
    ----------
    param_dict : Dict
        A dictionary containing the path and other parameters for reading the DataPackage. The path
        should point to the directory containing the DataPackage's YAML descriptor and CSV files.
    perform_checks : bool, optional
        If True (default), performs integrity checks on the DataPackage instance after reading it.

    Returns
    -------
    DataPackage
        The DataPackage instance read from the file system, with its tables and metadata populated.
    """

    package_name = param_dict["name"]

    if "path" in param_dict:
        fpackage = Package(
            Path(param_dict["path"]) / (package_name + ".datapackage.yaml")
        )
        metadata = fpackage.metadata_export()
        data = fpackage.extract()

        return_package = DataPackage(
            name=package_name,
            category_path=metadata["category_path"],
            version=metadata["version"],
            title=metadata["title"],
            comment=metadata["comment"],
            encoding=metadata["encoding"],
            target_language=metadata["target_language"],
            last_modified=metadata["last_modified"],
        )

        tables = {}
        for name, table in data.items():
            table_metadata = fpackage.get_resource(name).metadata_export()
            tabletype = table_metadata["tabletype"]
            field_metadata = None
            if "foreignKeys" in table_metadata["schema"]:
                field_metadata = table_metadata["schema"]["foreignKeys"]

            if tabletype == FactTable.type:
                tables[name] = FactTable.from_json(table, field_metadata)
            elif tabletype == AttributeTable.type:
                tables[name] = AttributeTable.from_json(
                    table,
                    field_metadata,
                    table_metadata["attribute_name"],
                    table_metadata["attribute_category"],
                )
        return_package.tables = tables

        license_metadata = metadata["license"]
        l = License(
            license_metadata["acronym"],
            license_metadata["full_name"],
            license_metadata["description"],
            license_metadata["link"],
        )

        source_metadata = metadata["source"]
        return_package.source = Source(
            source_metadata["reference"],
            source_metadata["encoding"],
            source_metadata["link"],
            source_metadata["authors"],
            source_metadata["institution"],
            source_metadata["type"],
            l,
            source_metadata["language"],
            source_metadata["link_doc"],
        )

        modified_by_data = metadata["modified_by"]
        authors = []
        for author in modified_by_data["authors"]:
            authors.append(
                Author(author["name"], author["affiliation"], author["e_mail"])
            )
        return_package.modified_by = ModifiedBy(
            authors,
            Algorithm(
                modified_by_data["algorithm"]["name"],
                modified_by_data["algorithm"]["version_number"],
            ),
        )

        return return_package
