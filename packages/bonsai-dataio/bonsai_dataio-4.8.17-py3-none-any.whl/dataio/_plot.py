"""Datapackage plot module of the dataio utility."""

import os
from logging import getLogger
from pathlib import Path

import pandas as pd
import yaml
from graphviz import Digraph

from .set_logger import set_logger

logger = getLogger("root")


def plot(
    full_path: str = None,
    overwrite: bool = False,
    log_name: str = None,
    export_png: bool = True,
    export_svg: bool = False,
    export_gv: bool = False,
):
    """Create entity-relation diagram from dataio.yaml file.

    Exports .gv config file and figures in and .svg and .png format

    GraphViz must be installed in computer, not only as Python package.

    Structure of the output erd configuration dictionary:

    First-level: key = datapackage name; value type : dictionary

    Second level: keys = table name; value type : pandas.DataFrame

    pandas.DataFrame index: table field names

    pandas.DataFrame columns:

    - type: str
    - primary: bool
    - foreign: bool
    - field: str (field of foreign key)
    - table: str (table of foreign key)
    - datapackage: str (datapackage of foreign key)
    - direction: str in ['forward', 'back'] (direction of arrow)
    - style: str in ['invis', 'solid'] (style of arrow)

    Parameters
    ----------
    full_path : str
      path to dataio.yaml file
    overwrite : bool
      whether to overwrite output files
    log_name : str
      name of log file, if None no log is set
    export_png : bool
      whether to export .png graphic file
    export_svg : bool
      whether to export .svg graphic file
    export_gv : bool
      whether to export .gv configuration file

    Returns
    -------
    dict
      erd configuration dictionary
    gv
      graphviz configuration object
    """
    logger.info("Started dataio plot")
    logger.info("Validate arguments")

    # validate input arguments
    for arg, typ in zip(
        ["full_path", "overwrite", "log_name", "export_png", "export_svg", "export_gv"],
        [(str, Path), bool, (str, type(None)), bool, bool, bool],
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
            "Metadata file not accessible at {full_path}\n"
            f"Current working directory is {os.getcwd()}"
        )
        raise FileNotFoundError

    # open log file
    if log_name is not None:
        set_logger(filename=log_name, path=full_path.parent, overwrite=overwrite)
        logger.info("Started dataio plot log file")
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

    logger.info("In case of uncaught exceptions validate dataio.yaml")
    config = configure(metadata)

    graph = generate(
        config, Path(full_path).with_suffix(""), export_png, export_svg, export_gv
    )

    logger.info("Finished dataio plot")

    return config, graph


def configure(metadata: dict):
    """Create diagram config dict based on dataio metadata dict.

    Parameter
    ----------
    metadata : dict
      dataio metadata

    Returns
    -------
    dict
      erd configuration dictionary
      - First-level keys are datapackage names
      - First-level values are dictionaries
      - Second-level keys are table names
      - Second-level values are data frames
        - index: field name
        - columns:
          - type: str
          - primary: bool
          - foreign: bool
          - field: str (foreign)
          - table: str (foreign)
          - datapackage: str (foreign)
          - direction: str in ['forward', 'back']
          - style: str in ['invis', 'solid']
    """
    logger.info("Started configure. Loading tables:")
    # metadata should be dictionary
    # it should contain keys ['name', 'tables'] of type [str, list]

    config = {metadata["name"]: {}}
    # Fill in information from each resource
    for position, resource in enumerate(metadata["tables"]):
        # resource is dict with keys ['name', 'schema'] of types [str, dict]
        logger.info(f"Table {resource['name']} in position {position}")
        table = load_schema(
            schema=resource["schema"],
            datapackage=metadata["name"],
            table=resource["name"],
        )
        config[metadata["name"]][resource["name"]] = table
    return config


def load_schema(schema: dict, datapackage: str, table: str):
    """Load and check validity of table schema.

    Parameters
    ----------
    schema : dict
      expected fields are fields, primaryKeys and foreignKeys
    datapackage : str
      name of current datapackage
    table : str
      name of current table

    Returns
    -------
    dataframe
      index: field names
      columns:
        - type: str
        - primary: bool
        - foreign: bool
        - field: str (foreign)
        - table: str (foreign)
        - datapackage: str (foreign)
        - direction: str in ['forward', 'back']
        - style: str in ['invis', 'solid']
    """
    logger.info("Started load_schema")

    # renaming to avoid clash
    resource = table

    table = pd.DataFrame()
    table.index = [field["name"] for field in schema["fields"]]
    table["type"] = [field["type"] for field in schema["fields"]]

    table["primary"] = False
    if "primaryKeys" in schema.keys():
        table["primary"].at[schema["primaryKeys"][0]] = True
    table["foreign"] = False
    table["field"] = None
    table["table"] = None
    table["datapackage"] = None
    table["direction"] = None
    table["style"] = None

    if "foreignKeys" in schema.keys():
        for foreign_key in schema["foreignKeys"]:
            index = foreign_key["fields"][0]
            table.loc[index, "foreign"] = True
            table.loc[index, "field"] = foreign_key["reference"]["fields"][0]

            if "table" in foreign_key["reference"].keys():
                table.loc[index, "table"] = foreign_key["reference"]["table"]
            else:
                table.loc[index, "table"] = resource

            if "datapackage" in foreign_key["reference"].keys():
                table.loc[index, "datapackage"] = foreign_key["reference"][
                    "datapackage"
                ]
            else:
                table.loc[index, "datapackage"] = datapackage

            if "direction" in foreign_key["reference"].keys():
                table.loc[index, "direction"] = foreign_key["reference"]["direction"]
            else:
                table.loc[index, "direction"] = "forward"

            if "style" in foreign_key["reference"].keys():
                table.loc[index, "style"] = foreign_key["reference"]["style"]
            else:
                table.loc[index, "style"] = "solid"

    logger.info("Finished load_schema")
    return table


def generate(config: dict, filepath: str, export_png, export_svg, export_gv):
    """Create entity-relation diagram.

    Exports .gv config file and figures in and .svg and .pdf format

    Parameter
    ---------
    config : dict
      - First-level keys are datapackages
      - First-level values are dictionaries
      - Second-level keys are tables
      - Second-level values are data frames.
    filepath : str
      path and stem of output files

    Results
    ---------
    graphviz.Digraph
    """
    full_graph = Digraph("G", filename=f"{filepath}.gv")
    full_graph.graph_attr["layout"] = "dot"
    full_graph.graph_attr["rankdir"] = "LR"
    full_graph.graph_attr["constraint"] = "true"
    full_graph.graph_attr["nodesep"] = "0.5"
    full_graph.graph_attr["ranksep"] = "1.2"

    # create nodes with full tables
    for pack_name, package in config.items():
        sub_graph = Digraph("cluster_" + pack_name)
        sub_graph.graph_attr["style"] = "dashed"
        sub_graph.graph_attr["label"] = pack_name
        for table_name, table in package.items():
            label = (
                f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n'
                f'\t<TR><TD ALIGN="LEFT" PORT="pk" COLSPAN="3" ><B>'
                f"{table_name}</B> \n\t</TD></TR>\n"
            )
            for field in table.index:
                if table["primary"].at[field]:
                    if table["foreign"].at[field]:
                        key = "PK/FK"
                    else:
                        key = "PK"
                else:
                    if table["foreign"].at[field]:
                        key = "FK"
                    else:
                        key = ""
                type_ = table["type"].at[field]
                port_left = field + "_left"
                port_right = field + "_right"
                label = label + (
                    f'\t<TR><TD ALIGN="LEFT" PORT="{port_left}">{key}</TD>\n'
                    f'\t\t<TD ALIGN="LEFT">{type_}</TD>\n'
                    f'\t\t<TD ALIGN="LEFT" PORT="{port_right}">{field}</TD>\n'
                    "\t</TR>\n"
                )
            label = label + ("</TABLE>>")
            sub_graph.node(f"{pack_name}_{table_name}", label=label, shape="none")
        full_graph.subgraph(sub_graph)

    # add missing data packages
    for pack_name, package in config.items():
        for table_name, table in package.items():
            for field in table.index:
                if table["foreign"].at[field]:
                    edge_direction = table["direction"].at[field]
                    parent_pack = table["datapackage"].at[field]
                    parent_table = table["table"].at[field]
                    parent_field = table["field"].at[field]
                    parent_type = table["type"].at[field]

                    if parent_pack not in config.keys():
                        # sub_graph.node(f'{parent_pack}_other',
                        #                label='...', shape='none')
                        # with full_graph.subgraph(
                        #    name=f'cluster_{pack_name}'
                        # ) as sub_graph:
                        with full_graph.subgraph(
                            name=f"cluster_{pack_name}_{parent_pack}"
                        ) as subsub_graph:
                            subsub_graph.graph_attr["style"] = "dashed"
                            subsub_graph.graph_attr["label"] = parent_pack

    # add missing tables
    for pack_name, package in config.items():
        for table_name, table in package.items():
            for field in table.index:
                if table["foreign"].at[field]:
                    edge_direction = table["direction"].at[field]
                    parent_pack = table["datapackage"].at[field]
                    parent_table = table["table"].at[field]
                    parent_field = table["field"].at[field]
                    parent_type = table["type"].at[field]

                    if parent_pack not in config.keys():
                        label = (
                            '<<TABLE BORDER="0" CELLBORDER="1" '
                            'CELLSPACING="0">\n'
                            '\t<TR><TD ALIGN="LEFT" PORT="pk" COLSPAN="3" ><B>'
                            f"{parent_table}</B> \n\t</TD></TR>\n"
                        )
                        port_left = parent_field + "_left"
                        port_right = parent_field + "_right"
                        label = label + (
                            f'\t<TR><TD ALIGN="LEFT" PORT="{port_left}">PK</TD>\n'
                            f'\t\t<TD ALIGN="LEFT">{parent_type}</TD>\n'
                            f'\t\t<TD ALIGN="LEFT" PORT="{port_right}">'
                            f"{parent_field}</TD>\n\t</TR>\n"
                        )
                        label = label + (
                            '\t<TR><TD ALIGN="LEFT">...</TD>\n'
                            '\t\t<TD ALIGN="LEFT">...</TD>\n'
                            '\t\t<TD ALIGN="LEFT">...</TD>\n'
                            "\t</TR>\n"
                        )
                        label = label + ("</TABLE>>")
                        # with full_graph.subgraph(
                        #     name=f'cluster_{pack_name}'
                        # ) as subgraph:
                        with full_graph.subgraph(
                            name=f"cluster_{pack_name}_{parent_pack}"
                        ) as subsubgraph:
                            subsubgraph.node(
                                f"{pack_name}_{parent_pack}_{parent_table}",
                                label=label,
                                shape="none",
                            )
                    else:
                        if parent_table not in config[parent_pack].keys():
                            label = (
                                '<<TABLE BORDER="0" CELLBORDER="1" '
                                'CELLSPACING="0">\n\t<TR><TD ALIGN="LEFT" '
                                'PORT="pk" COLSPAN="3" ><B>'
                                f"{parent_table}</B> \n\t</TD></TR>\n"
                            )
                            port_left = parent_field + "_left"
                            port_right = parent_field + "_right"
                            label = label + (
                                f'\t<TR><TD ALIGN="LEFT" PORT="{port_left}">PK</TD>\n'
                                f'\t\t<TD ALIGN="LEFT">{parent_type}</TD>\n'
                                f'\t\t<TD ALIGN="LEFT" PORT="{port_right}">'
                                f"{parent_field}</TD>\n\t</TR>\n"
                            )
                            label = label + (
                                '\t<TR><TD ALIGN="LEFT"></TD>\n'
                                '\t\t<TD ALIGN="LEFT">...</TD>\n'
                                '\t\t<TD ALIGN="LEFT">...</TD>\n'
                                "\t</TR>\n"
                            )
                            label = label + ("</TABLE>>")
                            with full_graph.subgraph(
                                name=f"cluster_{parent_pack}"
                            ) as subgraph:
                                subgraph.node(
                                    f"{parent_pack}_{parent_table}",
                                    label=label,
                                    shape="none",
                                )

    # add foreign key relations
    for pack_name, package in config.items():
        for table_name, table in package.items():
            for field in table.index:
                if table["foreign"].at[field]:
                    edge_direction = table["direction"].at[field]
                    parent_pack = table["datapackage"].at[field]
                    parent_table = table["table"].at[field]
                    parent_field = table["field"].at[field]
                    parent_type = table["type"].at[field]
                    edge_style = table["style"].at[field]

                    if parent_pack not in config.keys():
                        source_node, target_node = format_external(
                            pack_name,
                            table_name,
                            field,
                            parent_pack,
                            parent_table,
                            parent_field,
                            edge_direction,
                        )
                        full_graph.edge(source_node, target_node, dir=edge_direction)
                    elif (parent_table == table_name) and (parent_pack == pack_name):
                        source_node, target_node = format_self(
                            pack_name,
                            table_name,
                            field,
                            parent_pack,
                            parent_table,
                            parent_field,
                            edge_direction,
                        )
                        full_graph.edge(
                            source_node, target_node, dir=edge_direction, label=" "
                        )
                    else:
                        source_node, target_node = format_internal(
                            pack_name,
                            table_name,
                            field,
                            parent_pack,
                            parent_table,
                            parent_field,
                            edge_direction,
                        )
                        full_graph.edge(
                            source_node,
                            target_node,
                            dir=edge_direction,
                            style=edge_style,
                        )

    # full_graph.view()
    if export_svg:
        full_graph.render(filepath, view=False, format="svg")
    if export_png:
        full_graph.render(filepath, view=False, format="png")
    if export_gv:
        os.rename(filepath, f"{filepath}.gv")
    else:
        os.remove(filepath)
    return full_graph


def format_self(
    pack_name,
    table_name,
    field,
    parent_pack,
    parent_table,
    parent_field,
    edge_direction,
):
    """Format foreign key relation with same table."""
    if edge_direction == "forward":
        target_node = f"{pack_name}_{table_name}:{field}_left:w"
        source_node = f"{parent_pack}_{parent_table}:" f"{parent_field}_left:w"
    elif edge_direction == "back":
        source_node = f"{pack_name}_{table_name}:{field}_left:w"
        target_node = f"{parent_pack}_{parent_table}:" f"{parent_field}_left:w"
    else:
        raise KeyError("direction mandatory: forward or back")
    return source_node, target_node


def format_internal(
    pack_name,
    table_name,
    field,
    parent_pack,
    parent_table,
    parent_field,
    edge_direction,
):
    """Format foreign key relation with table in same data package."""
    if edge_direction == "forward":
        target_node = f"{pack_name}_{table_name}:{field}_left"
        source_node = f"{parent_pack}_{parent_table}:" f"{parent_field}_right"
    elif edge_direction == "back":
        source_node = f"{pack_name}_{table_name}:{field}_right"
        target_node = f"{parent_pack}_{parent_table}:" "{parent_field}_left"
    else:
        logger.error("direction mandatory: forward or back")
        raise KeyError
    return source_node, target_node


def format_external(
    pack_name,
    table_name,
    field,
    parent_pack,
    parent_table,
    parent_field,
    edge_direction,
):
    """Format foreign key relation with table in another data package."""
    if edge_direction == "forward":
        target_node = f"{pack_name}_{table_name}:{field}_left"
        source_node = (
            f"{pack_name}_{parent_pack}_{parent_table}:" f"{parent_field}_right"
        )
    elif edge_direction == "back":
        source_node = f"{pack_name}_{table_name}:{field}_right"
        target_node = f"{pack_name}_{parent_pack}_{parent_table}:" "{parent_field}_left"
    else:
        logger.error("direction mandatory: forward or back")
        raise KeyError
    return source_node, target_node
