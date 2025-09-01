"""Datapackage validate module of the dataio utility."""

import os
from logging import getLogger
from pathlib import Path
from pdb import set_trace

import frictionless
import pandas as pd
import yaml
from pydantic import BaseModel

import dataio.load as load
from dataio.schemas.bonsai_api.base_models import MatrixModel
from dataio.tools import BonsaiBaseModel

from .set_logger import set_logger

logger = getLogger("root")


def validate_matrix(df: pd.DataFrame, schema: MatrixModel):
    rows = df.index
    columns = df.columns

    schema.row_schema.to_dataclass(rows)
    schema.column_schema.to_dataclass(columns)


def validate_table(df: pd.DataFrame, schema: BonsaiBaseModel):
    if "code" in df.columns:
        # Check for duplicates in the specified column
        duplicates = df["code"].duplicated(keep=False)

        if duplicates.any():
            duplicate_values = df["code"][duplicates].unique()
            raise ValueError(
                f"Duplicate values found in column 'code': {duplicate_values}"
            )
    schema.to_dataclass(df)


def validate(full_path: str, overwrite: bool = False, log_name: str = None) -> dict:
    """Validate datapackage.

    Validates datapackage with metadata at:
    <full_path>=<root_path>/<path>/<name>.dataio.yaml

    Creates <name>.validate.yaml for frictionless validation
    and outputs dataio-specific validation to the log.

    Specific fields expected in <name>.dataio.yaml:

    - name : should match <name>
    - path : from which <path> is inferred
    - version

    Parameters
    ----------
    full_path : str
      path to dataio.yaml file
    overwrite : bool
      whether to overwrite output files
    log_name : str
      name of log file, if None no log is set

    Returns
    -------
    dict
      frictionless validate report dictionary
    """
    n_errors = 0

    logger.info("Started dataio describe")
    logger.info("Started dataio validate")
    logger.info("Validate arguments")

    # validate input arguments
    for arg, typ in zip(
        ["full_path", "overwrite", "log_name"], [(str, Path), bool, (str, type(None))]
    ):
        if not isinstance(locals()[arg], typ):
            logger.error(
                f"argument {arg} is of type {type(locals()[arg])}" f" != {typ}"
            )
            raise TypeError

    # validate path
    logger.info("Validate path")
    full_path = Path(full_path)
    if full_path.name[-12:] != ".dataio.yaml":
        logger.error(f"Full path suffix is not '.dataio.yaml': {full_path}")
        raise FileNotFoundError
    datapackage_name = full_path.name[:-12]

    if not os.path.exists(str(full_path)):
        logger.error(
            f"Metadata file not accessible at {full_path}\n"
            f"Current working directory is {os.getcwd()}"
        )
        raise FileNotFoundError

    # open log file
    if log_name is not None:
        set_logger(filename=log_name, path=full_path.parent, overwrite=overwrite)
        logger.info("Started dataio validate log file")
    else:
        logger.info("Not initialized new log file")

    # read dataio datapackage metadata
    try:
        with open(full_path, "r") as f:
            metadata = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Could not open dataio datapackage metadata file " f"{full_path}")
        raise
    logger.info(f"Dataio datapackage metadata file opened at {full_path}")
    logger.info("Validating general features")

    # check dataio datapackage specific fields
    for key in ["name", "path", "version"]:
        if key not in metadata.keys():
            logger.error(f"Key {key} missing from metadata")
            n_errors += 1
        if not isinstance(metadata[key], str):
            logger.error(
                f"metadata['{key}'] is of type " f"{type(metadata[key])} != {str}"
            )
            n_errors += 1
    for whitespace in [" ", "\n", "\t"]:
        if whitespace in metadata["name"]:
            logger.error(f"Metadata name '{metadata['name']}' has whitespace")
            n_errors += 1

    if metadata["name"] != datapackage_name:
        logger.error(
            "Name of metadata file and datapackage name do not "
            f"match: {metadata['name']} != {datapackage_name}"
        )
        n_errors += 1

    # check datapackages
    parent_datapackages = {}

    if metadata["path"] == ".":
        root_path = str(Path(full_path).parent)
    else:
        root_path = str(Path(full_path).parent)[: -len(metadata["path"])]
    logger.info(f"root_path is '{root_path}'")

    if "datapackages" not in metadata.keys():
        logger.info("Key 'datapackages' not found in metadata")
    else:
        logger.info("Found key 'datapackages' in metadata")
        if not isinstance(metadata["datapackages"], list):
            logger.error(
                "Type of metadata 'datapackages' is "
                f"{type(metadata['datapackages'])} and not 'list'"
            )
            n_errors += 1
        else:
            for datapackage in metadata["datapackages"]:
                for key in ["name", "path", "version"]:
                    if key not in datapackage.keys():
                        logger.error(f"Key {key} missing from datapackage")
                        n_errors += 1
                    if not isinstance(datapackage[key], str):
                        logger.error(
                            f"datapackage['{key}'] is of type "
                            f"{type(datapackage[key])} != {str}"
                        )
                        n_errors += 1
                for whitespace in [" ", "\n", "\t"]:
                    if whitespace in datapackage["name"]:
                        logger.error(
                            f"Datapackage '{datapackage['name']}' has whitespace"
                        )
                        n_errors += 1

                if datapackage["name"] == datapackage_name:
                    logger.error(
                        "Name of metadata file and external datapackage "
                        f"match: {datapackage_name}"
                    )
                    n_errors += 1

                # load datapackage
                parent_path = (
                    Path(root_path)
                    .joinpath(datapackage["path"])
                    .joinpath(f"{datapackage['name']}.dataio.yaml")
                )
                logger.info(
                    "Loading metadata of datapackage "
                    f"'{datapackage['name']}' at "
                    f"path '{parent_path}'"
                )
                parent_datapackages[datapackage["name"]] = load(
                    full_path=parent_path, include_tables=False
                )

                # check version
                parent_version = parent_datapackages[datapackage["name"]].__metadata__[
                    "version"
                ]
                if datapackage["version"] != parent_version:
                    logger.error(
                        "Version of expected and external datapackage "
                        "versions do not match:\n"
                        f"name: {datapackage['name']}\n"
                        f"expected version: {datapackage['version']}\n"
                        f"found version: {parent_version}"
                    )
                    n_errors += 1

    if "tables" not in metadata.keys():
        logger.error("Key 'tables' missing from metadata")
        n_errors += 1
    if not isinstance(metadata["tables"], list):
        logger.error(
            f"metadata['tables'] is of type " f"{type(metadata['tables'])} != {list}"
        )
        n_errors += 1

    # check tables
    logger.info("General features validated")
    for position, resource in enumerate(metadata["tables"]):
        logger.info(f"Validating specific features of table {position}")
        for key in ["name", "path", "tabletype"]:
            if key not in resource.keys():
                logger.error(f"Key '{key}' missing from table {position}")
                n_errors += 1
            if not isinstance(resource[key], str):
                logger.error(
                    f"Key {key} is of type {type(resource[key])} != "
                    f"{str} in table {position}"
                )
                n_errors += 1

        logger.info(
            f"Name = '{resource['name']}' , path = "
            f"'{resource['path']}', tabletype = "
            f"'{resource['tabletype']}'"
        )
        # name
        for whitespace in [" ", "\n", "\t"]:
            if whitespace in resource["name"]:
                logger.error(f"Metadata name '{resource['name']}' has whitespace")
                n_errors += 1

        # tabletype
        tabletype_list = ["fact", "dimension", "tree", "concordance", "other"]
        if resource["tabletype"] not in tabletype_list:
            logger.error(
                f"Field 'tabletype' of resource {position} with "
                f"name {resource['name']} is "
                f"{resource['tabletype']}, which is not is "
                f"{tabletype_list}"
            )
            n_errors += 1
        logger.info(f"Specific features of resource {position} validated")

    # foreign keys
    resource_names = [resource["name"] for resource in metadata["tables"]]
    resource_types = [resource["tabletype"] for resource in metadata["tables"]]
    for resource in metadata["tables"]:
        logger.info("Validating foreign keys of resource " f"{resource['name']}")

        schema, n_errors = validate_schema(resource, n_errors)
        field_names = [field["name"] for field in schema["fields"]]
        field_types = [field["type"] for field in schema["fields"]]
        if "primaryKeys" not in schema.keys():
            logger.warning("Primary key not found, no checks performed")
        else:
            primary_key = schema["primaryKeys"][0]
            if len(field_names) != len(set(field_names)):
                logger.error(f"Repeated field names: {field_names}")
                n_errors += 1

            if primary_key not in field_names:
                logger.error(
                    f"Unrecognized primary key {primary_key}, not in " f"{field_names}"
                )
                n_errors += 1

            if field_types[field_names.index(primary_key)] not in ["string"]:
                logger.error(f"Primary key {primary_key} type is not in " "['string']")
                n_errors += 1

        if "foreignKeys" not in schema.keys():
            logger.warning("Foreign keys not found, no checks performed")
        else:
            foreign_key_children = [
                field["fields"][0] for field in schema["foreignKeys"]
            ]
            foreign_key_parents = [
                field["reference"]["fields"][0] for field in schema["foreignKeys"]
            ]
            foreign_key_tables = [
                (
                    field["reference"]["table"]
                    if "table" in field["reference"].keys()
                    else resource["name"]
                )
                for field in schema["foreignKeys"]
            ]

            foreign_key_datapackages = [
                (
                    field["reference"]["datapackage"]
                    if "datapackage" in field["reference"].keys()
                    else datapackage_name
                )
                for field in schema["foreignKeys"]
            ]

            if len(foreign_key_children) != len(set(foreign_key_children)):
                logger.error("Repeated foreign key fields: " f"{foreign_key_children}")
                n_errors += 1

        resource["schema"] = schema

        # generic constraints
        if resource["tabletype"] != "other":
            if "id" not in field_names:
                logger.error("Field 'id' expected if tabletype != 'other'")
                n_errors += 1
            for field_name in field_names:
                if field_name not in [
                    "id",
                    "value",
                    "name",
                    "description",
                    "comment",
                    "position",
                ]:
                    if field_name not in foreign_key_children:
                        logger.warning(
                            f"Field '{field_name}' should have a "
                            "foreign key relation"
                        )
            if "foreignKeys" in schema.keys():
                for position, table in enumerate(foreign_key_tables):
                    if (table not in resource_names) and (
                        foreign_key_datapackages[position] == datapackage_name
                    ):
                        logger.warning(
                            f"Table {table} reference in foreign key "
                            f"{position} does not exist in datapackage"
                        )
                    if foreign_key_parents[position] != "id":
                        logger.error(
                            f"Parent field referenced in foreign key "
                            f"{position} is "
                            f"{foreign_key_parents[position]} != 'id'"
                        )
                        n_errors += 1

        # tabletype specific constraints
        if resource["tabletype"] == "fact":
            if "value" not in field_names:
                logger.error("Field 'value' expected if tabletype = 'fact'")
                n_errors += 1
            else:
                if field_types[field_names.index("value")] != "number":
                    logger.error(
                        "Field 'value' expected to have type 'number' instead of "
                        f"{field_types[field_names.index('value')]}"
                    )
                    n_errors += 1
        elif resource["tabletype"] == "dimension":
            if "position" not in field_names:
                logger.error("Field 'position' expected if tabletype = " "'dimension'")
                n_errors += 1
            else:
                if field_types[field_names.index("position")] != "integer":
                    logger.error(
                        "Field 'position' expected to have type 'integer' instead "
                        f"of {field_types[field_names.index('position')]}"
                    )
                    n_errors += 1
        elif resource["tabletype"] == "tree":
            if "parent_id" not in field_names:
                logger.error("Field 'parent_id' expected if tabletype = " "'tree'")
                n_errors += 1
            else:
                if (
                    foreign_key_tables[foreign_key_children.index("parent_id")]
                    != resource["name"]
                ):
                    logger.error("Field 'parent_id' expected if tabletype = " "'tree'")
                    n_errors += 1
        elif resource["tabletype"] == "concordance":
            if len(foreign_key_tables) != 2:
                logger.error(
                    "Two foreign keys expected if tabletype = " "'concordance'"
                )
                n_errors += 1
    logger.info("DataIO table constraints validation finished")

    if n_errors > 0:
        logger.error(f"{n_errors} errors found, validation aborted")
        raise TypeError

    logger.info("DataIO metadata validated, no errors found")

    # check dialect
    for table in metadata["tables"]:
        if "dialect" in table.keys():
            logger.info(f"Table {table['name']} has 'dialect' field")
            if "csv" in table["dialect"].keys():
                logger.info(f"Table {table['name']} 'dialect' has 'csv' field")
                dialect = table["dialect"]["csv"]
                if "delimiter" in dialect.keys():
                    logger.warning(
                        f"Table {table['name']} field ['dialect']['csv']"
                        f"['delimiter'] = {dialect['delimiter']}"
                    )
                if "quoteChar" in dialect.keys():
                    logger.warning(
                        f"Table {table['name']} field ['dialect']['csv']"
                        f"['quoteChar'] = {dialect['quoteChar']}"
                    )
                if "skipInitialSpace" in dialect.keys():
                    logger.warning(
                        f"Table {table['name']} field ['dialect']['csv']"
                        f"['skipInitialSpace'] = {dialect['skipInitialSpace']}"
                    )
                    if dialect["skipInitialSpace"]:
                        logger.warning(
                            "This might raise problems loading if there are "
                            "delimiters inside quoted strings"
                        )

    # shift path to tables
    for tab_pos, table in enumerate(metadata["tables"]):
        if metadata["path"] != ".":
            table["path"] = str(Path(metadata["path"]).joinpath(table["path"]))
        metadata["tables"][tab_pos] = table

    # fix refs to tables from other datapackages
    to_add = {}
    for tab_pos, table in enumerate(metadata["tables"]):
        schema = table["schema"]
        if "foreignKeys" in schema.keys():
            for pos, foreign_key in enumerate(schema["foreignKeys"]):
                if "datapackage" in foreign_key["reference"].keys():
                    parent_datapackage = foreign_key["reference"]["datapackage"]
                    parent_table = foreign_key["reference"]["table"]
                    logger.info(
                        "Found foreign key to datapackage "
                        f"{parent_datapackage} and table {parent_table}"
                    )
                    if parent_datapackage not in to_add.keys():
                        to_add[parent_datapackage] = []
                    if parent_table not in to_add[parent_datapackage]:
                        to_add[parent_datapackage].append(parent_table)
                    del schema["foreignKeys"][pos]["reference"]["datapackage"]
                    schema["foreignKeys"][pos]["reference"][
                        "table"
                    ] = f"{parent_datapackage}_{parent_table}"
        table["schema"] = schema
        metadata["tables"][tab_pos] = table

    # add tables from other datapackages
    for parent_datapackage, parent_tables in to_add.items():
        table_positions = {}
        tables = parent_datapackages[parent_datapackage].__metadata__["tables"]
        for pos, table in enumerate(tables):
            table_positions[table["name"]] = pos
        for parent_tablename in parent_tables:
            tmp = tables[table_positions[parent_tablename]]
            tmp["name"] = f"{parent_datapackage}_{parent_tablename}"
            tmp["path"] = str(
                Path(
                    parent_datapackages[parent_datapackage].__metadata__["path"]
                ).joinpath(tmp["path"])
            )
            del tmp["schema"]["foreignKeys"]
            metadata["tables"].append(tmp)

    # rename table to resource
    metadata["resources"] = metadata["tables"]
    del metadata["tables"]
    for res_pos, resource in enumerate(metadata["resources"]):
        if "foreignKeys" in resource["schema"].keys():
            for fk_pos, foreignkey in enumerate(resource["schema"]["foreignKeys"]):
                if "table" in foreignkey["reference"].keys():
                    foreignkey["reference"]["resource"] = foreignkey["reference"][
                        "table"
                    ]
                    del foreignkey["reference"]["table"]
                resource["schema"]["foreignKeys"][fk_pos] = foreignkey
            metadata["resources"][res_pos] = resource

    # apply frictionless
    logger.info("Starting frictionless validate")
    frictionless_yaml = str(
        Path(root_path).joinpath(f"{datapackage_name}.datapackage.yaml")
    )
    if not overwrite:
        if os.path.isfile(frictionless_yaml):
            logger.error(
                f"File {frictionless_yaml} already exists and "
                "'overwrite' option is {overwrite}"
            )
            raise FileExistsError

    # set_trace()
    with open(frictionless_yaml, "w") as f:
        yaml.safe_dump(metadata, f)
    report = frictionless.validate(frictionless_yaml)

    report_yaml = Path(full_path).with_stem(f"{datapackage_name}.validate")
    if not overwrite:
        if os.path.isfile(report_yaml):
            logger.error(
                f"File {report_yaml} already exists and "
                "'overwrite' option is {overwrite}"
            )
            raise FileExistsError
    with open(report_yaml, "w") as f:
        yaml.safe_dump(report.to_dict(), f)

    os.remove(frictionless_yaml)

    if report.stats["errors"] > 0:
        frictionless_errors = report.stats["errors"]
        logger.error(
            f"{frictionless_errors} errors related to frictionless found, validation aborted"
        )
        raise TypeError

    logger.info("Finished frictionless validate")
    return report.to_dict()


def validate_schema(resource, n_errors):
    """Check if schema, fields, primary and foreign keys exist."""
    # schema
    if "schema" not in resource.keys():
        logger.error("Key 'schema' missing from table keys")
        n_errors += 1
    schema = resource["schema"]
    if not isinstance(schema, dict):
        logger.error(f"Schema is of type {type(schema)} != " f"{dict}")
        n_errors += 1
    for key in ["fields", "foreignKeys", "primaryKeys"]:
        if key not in schema.keys():
            if key == "foreignKeys":
                logger.warning(f"Key '{key}' missing from table['schema'] keys")
            elif key == "primaryKeys":
                logger.warning(f"Key '{key}' missing from table['schema'] keys")
            else:
                logger.error(f"Key '{key}' missing from table['schema'] keys")
                n_errors += 1
        elif not isinstance(schema[key], list):
            logger.error(f"Key {key} is of type {type(schema[key])} != " f"{list}")
            n_errors += 1

    # fields
    for pos, field in enumerate(schema["fields"]):
        for key in ["name", "type"]:
            if key not in field.keys():
                logger.error(f"Key '{key}' missing from {pos} field")
                n_errors += 1
            elif not isinstance(field[key], str):
                logger.error(
                    f"Key {key} in {pos} field is of type "
                    "{type(field[key])} != {str}"
                )
                n_errors += 1
        if "name" in field.keys():
            for whitespace in [" ", "\n", "\t"]:
                if whitespace in field["name"]:
                    logger.error(f"Field {pos} 'name' has whitespace")
                    n_errors += 1

        if "type" in field.keys():
            # needs to be aligned with create!!!!
            fric_list = ["number", "integer", "boolean", "string", "datetime"]
            if field["type"] == "any":
                logger.warning(
                    f"Found 'any' type in in field {pos}. " "Changed to 'str'"
                )
                field["type"] = "string"
                schema["fields"][pos] = field
            if field["type"] not in fric_list:
                logger.error(
                    f"Invalid type in field {pos}. Accepted types are " f"{fric_list}."
                )
                n_errors += 1

    # primary keys
    if "primaryKeys" in schema.keys():
        if len(schema["primaryKeys"]) > 1:
            logger.error(f"Multiple primary keys: {schema['primaryKeys']}")
            n_errors += 1

    # foreign keys
    if "foreignKeys" in schema.keys():
        for position, foreign_key in enumerate(schema["foreignKeys"]):
            for key, typ in zip(["fields", "reference"], [list, dict]):
                if key not in foreign_key.keys():
                    logger.error(
                        f"Field '{key}' missing from foreign key " "{position}"
                    )
                    n_errors += 1
                if not isinstance(foreign_key[key], typ):
                    logger.error(
                        f"Field '{key}' is of type "
                        f"{type(foreign_key[key])} != {typ}"
                    )
                    n_errors += 1

            if len(foreign_key["fields"]) != 1:
                logger.error(
                    f"Multiple local fields in foreign key {position}:"
                    f" {foreign_key['fields']}"
                )
                n_errors += 1

            if "fields" not in foreign_key["reference"].keys():
                logger.error(
                    "Field 'fields' missing from foreign key " f"{position} reference"
                )
                n_errors += 1
            if not isinstance(foreign_key["reference"]["fields"], list):
                logger.error(
                    f"Field 'fields' om foreign key reference is of "
                    f"type {type(foreign_key['reference']['fields'])} "
                    "!= {list}"
                )
                n_errors += 1

            if len(foreign_key["reference"]["fields"]) != 1:
                logger.error(
                    f"Multiple local fields in foreign key {position}:"
                    f" {foreign_key['reference']['fields']}"
                )
                n_errors += 1

    # check and remove entity-relation diagram keys
    directions = ["forward", "back"]
    styles = ["solid", "invis"]
    if "foreignKeys" in schema.keys():
        for position, foreign_key in enumerate(schema["foreignKeys"]):
            reference = foreign_key["reference"]
            # direction
            if "direction" in reference.keys():
                if not isinstance(reference["direction"], str):
                    logger.error(
                        f"Type of 'direction' is {type(reference['direction'])} is "
                        f"not {str} in foreign key {position}"
                    )
                    n_errors += 1
                if reference["direction"] not in directions:
                    logger.error(
                        f"Value of direction is {reference['direction']} and should "
                        f"be in {directions}"
                    )
                    n_errors += 1
                logger.info(
                    "Found entity relation diagram attribute 'direction' "
                    f"at position {position}. Removed for the purpose of "
                    "frictionless validate"
                )
                del schema["foreignKeys"][position]["reference"]["direction"]
            # style
            if "style" in reference.keys():
                if not isinstance(reference["style"], str):
                    logger.error(
                        f"Type of 'style' is {type(reference['style'])} is not"
                        f" {str} in foreign key {position}"
                    )
                    n_errors += 1
                if reference["style"] not in styles:
                    logger.error(
                        f"Value of 'style' is {reference['style']} and should "
                        f"be in {styles}"
                    )
                    n_errors += 1
                logger.info(
                    "Found entity relation diagram attribute 'style' "
                    f"at position {position}. Removed for the purpose of "
                    "frictionless validate"
                )
                del schema["foreignKeys"][position]["reference"]["style"]

    return schema, n_errors
