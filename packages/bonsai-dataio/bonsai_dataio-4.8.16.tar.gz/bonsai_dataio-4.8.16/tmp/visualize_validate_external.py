"""Visualize module of the dataio utility."""
import os
from logging import getLogger
from pathlib import Path

import pandas as pd
import yaml
from graphviz import Digraph
from templates import set_logger

logger = getLogger('root')


def visualize(path: str = None,
              overwrite: bool = False,
              auto_log: bool = True,
              log_name: str = "visualize.log"):
  """Create entity-relation diagram from dataio.yaml file.

  Exports .gv config file and figures in and .svg and .pdf format

  GraphViz must be installed in computer, not only as Python package.

  Parameters
  ----------
  path : str
    path to dataio.yaml file
  overwrite : bool
    whether to overwrite output files
  auto_log : bool
    whether to initialize logger
  log_name : str
    name of log file


  Returns
  -------
  dict
    erd configuration dictionary
    - First-level keys are datapackages
    - First-level values are dictionaries
    - Second-level keys are tables
    - Second-level values are data frames.
  gv
    graphviz configuration object
  """
  if auto_log:
    set_logger()
  logger.info("Started dataio visualize")
  logger.info("Validate arguments")

  # validate input arguments
  for arg, typ in zip(
      ['path', 'overwrite', 'auto_log', 'log_name'],
      [str, bool, bool, str]):
    if not isinstance(locals()[arg], typ):
      logger.error(f"argument {arg} is of type {locals()[arg]} != "
                   f"{typ}")
      raise TypeError

  # validate path
  logger.info("Validate path")
  if not os.path.exists(str(Path(path).parent)):
    logger.error("Folder '{path}' not accessible from current "
                 f"working directory '{os.getcwd()}'")
    raise FileNotFoundError

  if auto_log:
    log_str = str(Path(path).with_name(log_name))
    if not overwrite:
      if os.path.exists(log_str):
        logger.error(f"File {log_str} already exists and "
                     "'overwrite' option is {overwrite}")
        raise FileExistsError
    set_logger(filename=log_name, path=Path(path).parent)
    logger.info("Started dataio visualize log file")

  # read dataio datapackage metadata
  try:
    with open(path, "r") as f:
      metadata = yaml.safe_load(f)
  except FileNotFoundError:
    logger.error("Could not open dataio datapackage metadata file "
                 f"{path}.")
  logger.info(f"Dataio datapackage metadata file opened at {path}")

  logger.info("In case of uncaught exceptions validate dataio.yaml")
  config = configure(metadata)

  graph = generate(config, Path(path).with_suffix(''))

  logger.info("Finished dataio visualize")

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
    refactored for ease of access
  """
  logger.info("Started configuring plot. Loading tables:")
  # metadata should be dictionary
  # it should contain keys ['name', 'resources'] of type [str, list]

  config = {metadata['name']: {}}
  # Fill in information from each resource
  for res_pos, resource in enumerate(metadata['resources']):
    # resource is dict with keys ['name', 'schema'] of types [str, dict]
    logger.info(f"Table {resource['name']} in position {res_pos}")
    table = load_resource(resource, res_pos)
    config[metadata['name']][resource['name']] = table

  logger.info("Checking for external references in foreign keys:")
  for res_pos, resource in enumerate(metadata['resources']):
    logger.info(f"Table {resource['name']} in position {res_pos}")
    table = config[metadata['name']][resource['name']]
    # check for external datapackages/tables/fields
    for index in table[table['foreign']].index:
      # found external datapackage
      if table['package'][index] not in config.keys():
        config[table['package'][index]] = {}
        new_table = pd.DataFrame(index=[table['field'][index]])
        new_table['type'] = table['type'][index]
        new_table['primary'] = True
        new_table['foreign'] = False
        new_table['field'] = None
        new_table['table'] = None
        new_table['package'] = None
        new_table['direction'] = None
        new_table['style'] = None
        config[table['package'][index]][table['table'][index]] = (
          new_table)
        logger.info(
          f"Added foreign datapackage {table['package'][index]}: "
          f"{new_table}")
      else:
        # found unknown table in external datapackage
        if (table['table'][index] not in
            config[table['package'][index]].keys()):
          # making sure it is not the current datapackage:
          if table['table'][index] != metadata['name']:
            new_table = pd.DataFrame(index=[table['field'][index]])
            new_table['type'] = 'string'
            new_table['primary'] = True
            new_table['foreign'] = False
            new_table['field'] = None
            new_table['table'] = None
            new_table['package'] = None
            new_table['direction'] = None
            new_table['style'] = None
            config[table['package'][index]
                   ][table['table'][index]] = new_table
            logger.info("Added table to datapackage "
                        f"{table['package'][index]}: {new_table}")
          else:
            logger.error("Something went wrong, missing link to current"
                         f"data package: {table[index]}")
        else:
          # found unknown field in existing table in external package
          if table['field'][index] not in config[
             table['package'][index]
             ][table['table'][index]].index:
            new_record = {'type':}

            config[table['package'][index]
                   ][table['table'][index]][table['field'][index]] = (
                     new_record)


            logger.info(
              f'Package {pack_name}, table {table_name} '
              f'field {index} references unknown parent '
              f"field {table['field'][index]}"
            )
            raise KeyError
          if table['direction'][index] not in ['forward', 'back']:
            logger.error(f'Package {pack_name}, table {table_name} '
                         f'field {index} references unknown parent '
                         f"direction {table['direction'][index]},"
                         ' should be in ["forward","back"]')
            raise KeyError
          if table['distance'][index] < 0:
            logger.error(f'Package {pack_name}, table {table_name} '
                         f'field {index} references negative '
                         f"distance")
            raise KeyError
  return config


def load_resource(resource, resource_position):
  """Load and check validity of resource.

  Parameters
  ----------
  resource : dict
    expected fields are schema, primaryKeys and foreignKeys
  resource_position : int
    used for error display

  Returns
  -------
  dataframe
    index are field names
    columns are 'type', 'primary', 'foreign', 'field',
    'parent_package', 'parent_field', 'parent_direction', 'n_ghosts'
  """
  res_pos = resource_position

  name_values = []
  type_values = []
  keys = ['fields', 'primaryKeys']
  types = [list, list]
  for key, type_ in zip(keys, types):
    if key not in resource['schema'].keys():
      logger.error(f'Configuration "resources({res_pos})/schema" '
                   'misses key {key}')
      raise KeyError
    if not isinstance(resource['schema'][key], type_):
      logger.error(f'Configuration "resources({res_pos})/schema"'
                   ' {key} is not of type {type_}')
      raise TypeError
  # Check existence and type of fields
  for field_pos, field in enumerate(resource['schema']['fields']):
    if not isinstance(field, dict):
      logger.error(f'Configuration "resources({res_pos})/schema/'
                   f'field({field_pos})" is not dict')
      raise TypeError
    keys = ['name', 'type']
    types = [str, str]
    for key, type_ in zip(keys, types):
      if key not in field.keys():
        logger.error(f'Configuration "resources({res_pos})/'
                     f'schema/fields(field_pos)" misses key '
                     f'{key}')
        raise KeyError
      if not isinstance(field[key], type_):
        logger.error(f'Configuration "res_pos({res_pos})/'
                     f'schema/fields(field_pos)" key {key} is '
                     f'not of type {type_}')
        raise TypeError
    name_values.append(field['name'])
    type_values.append(field['type'])

  if len(name_values) != len(set(name_values)):
    logger.error(f'Configuration "resources({res_pos})/'
                 f'schema" field names are not unique')
    raise KeyError
  table = pd.DataFrame()
  table.index = name_values
  table['type'] = type_values

  # Check existence and type of primary keys
  if len(resource['schema']['primaryKeys']) != 1:
    raise ValueError(f'Configuration "resources({res_pos})/schema/ '
                     'length of primary key is not one:'
                     f"{len(resource['schema']['primaryKeys'])}.")
  if resource['schema']['primaryKeys'][0] not in table.index:
    raise ValueError('Invalid primary key: '
                     "{resource['schema']['primaryKeys'][0]}.")

  table['primary'] = False
  table['primary'].at[resource['schema']['primaryKeys'][0]] = True

  table['foreign'] = False
  table['field'] = None
  table['table'] = None
  table['package'] = None
  table['direction'] = None
  table['distance'] = None
  table['style'] = None

  # Check existence and type of foreign keys
  if 'foreignKeys' in resource['schema'].keys():
    if not isinstance(resource['schema']['foreignKeys'], list):
      raise TypeError(f'Configuration "resources({res_pos})/schema/'
                      'foreignKeys" is not list')

    for key_pos, foreign in enumerate(
        resource['schema']['foreignKeys']):
      if not isinstance(foreign, dict):
        raise TypeError(f'Configuration "resources({res_pos})/schema/'
                        f'foreignKeys({key_pos})" is not dict')
      keys = ['fields', 'reference']
      types = [list, dict]
      for key, type_ in zip(keys, types):
        if key not in foreign.keys():
          raise KeyError(f'Configuration "resources({res_pos})/'
                         f'schema/foreignKeys({key_pos})" misses key '
                         f'{key}')
        if not isinstance(foreign[key], type_):
          raise TypeError(f'Configuration "resources({res_pos})/'
                          f'schema/foreignKeys({key_pos})" key {key} '
                          f'is not of type {type_}')

      # fields and resource
      if 'fields' not in foreign['reference'].keys():
        raise KeyError(f'Configuration "resources({res_pos})/'
                       f'schema/foreignKeys({key_pos})/reference" '
                       f'misses key "fields"')
      if not isinstance(foreign['reference']['fields'], list):
        raise TypeError(f'Configuration "resources({res_pos})/'
                        f'schema/foreignKeys({key_pos})/reference" '
                        f'key "fields" is not of type "list"')

      if 'resource' not in foreign['reference'].keys():
        foreign['reference']['resource'] = resource['name']
      if not isinstance(foreign['reference']['resource'], str):
        raise TypeError(f'Configuration "resources({res_pos})/'
                        f'schema/foreignKeys({key_pos})/reference" '
                        f'key "resource" is not of type "str"')

      # field in child table
      if len(foreign['fields']) != 1:
        raise ValueError(f'Configuration "resources({res_pos})/'
                         f'schema/foreignKeys({key_pos})/field'
                         f'length is not one: '
                         f'{len(foreign["fields"])}.')

      if foreign['fields'][0] not in table.index:
        raise ValueError(f'Configuration "resources({res_pos})/'
                         f'schema/foreignKeys({key_pos})/field '
                         'invalid foreign key child field: '
                         f"{foreign['fields'][0]}.")

      if len(foreign['reference']['fields']) != 1:
        raise ValueError(f'Configuration "resources({res_pos})/'
                         f'schema/foreignKeys({key_pos})/reference/'
                         f'fields length is not one: '
                         f'{len(foreign["reference"]["fields"])}.')

      table['foreign'].at[foreign['fields'][0]] = True
      table['field'].at[foreign['fields'][0]] = (
        foreign['reference']['fields'][0]
      )
      table['table'].at[foreign['fields'][0]] = (
        foreign['reference']['resource']
      )
      if 'package' in foreign['reference'].keys():
        if not isinstance(foreign['reference']['package'],
                          str):
          raise TypeError(f'Configuration "resources({res_pos})/'
                          f'schema/foreignKeys({key_pos})/reference" '
                          f'package is not of type str')
      else:
        foreign['reference']['package'] = resource['package']
      table['package'].at[foreign['fields'][0]] = (
        foreign['reference']['package']
      )
      if 'direction' in foreign['reference'].keys():
        if not isinstance(foreign['reference']['direction'],
                          str):
          raise TypeError(f'Configuration "resources({res_pos})/'
                          f'schema/foreignKeys({key_pos})/reference" '
                          f'direction is not of type str')
      else:
        foreign['reference']['direction'] = 'forward'
      table['direction'].at[foreign['fields'][0]] = (
        foreign['reference']['direction']
      )
      if 'distance' in foreign['reference'].keys():
        if not isinstance(foreign['reference']['distance'],
                          int):
          raise TypeError(f'Configuration "resources({res_pos})/'
                          f'schema/foreignKeys({key_pos})/reference'
                          f'"distance" is not of type int')
      else:
        foreign['reference']['distance'] = 0
      table['distance'].at[foreign['fields'][0]] = (
        foreign['reference']['distance']
      )
      if 'style' in foreign['reference'].keys():
        if not isinstance(foreign['reference']['style'],
                          str):
          raise TypeError(f'Configuration "resources({res_pos})/'
                          f'schema/foreignKeys({key_pos})/reference'
                          f'"style" is not of type str')
        if foreign['reference']['style'] != 'invis':
          raise ValueError(f'Configuration "resources({res_pos})/'
                           f'schema/foreignKeys({key_pos})/reference'
                           f'"style" value is not "invis"')
      else:
        foreign['reference']['style'] = 'solid'
      table['style'].at[foreign['fields'][0]] = (
        foreign['reference']['style']
      )

  return table


def generate(database, filepath):
  """Create entity-relation diagram.

  Exports .gv config file and figures in and .svg and .pdf format

  Parameter
  ---------
  database : dict
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
  full_graph = Digraph('G', filename=f'{filepath}.gv')
  full_graph.graph_attr['layout'] = 'dot'
  full_graph.graph_attr["rankdir"] = 'LR'
  full_graph.graph_attr['constraint'] = 'true'
  full_graph.graph_attr['nodesep'] = '0.5'
  full_graph.graph_attr['ranksep'] = '1.2'

  # create nodes with full tables
  for pack_name, package in database.items():
    sub_graph = Digraph('cluster_' + pack_name)
    sub_graph.graph_attr["style"] = "dashed"
    sub_graph.graph_attr["label"] = pack_name
    for table_name, table in package.items():
      label = (f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n'
               f'\t<TR><TD ALIGN="LEFT" PORT="pk" COLSPAN="3" ><B>'
               f'{table_name}</B> \n\t</TD></TR>\n')
      for field in table.index:
        if table['primary'].at[field]:
          if table['foreign'].at[field]:
            key = 'PK/FK'
          else:
            key = 'PK'
        else:
          if table['foreign'].at[field]:
            key = 'FK'
          else:
            key = ''
        type_ = table['type'].at[field]
        port_left = field + '_left'
        port_right = field + '_right'
        label = label + (
          f'\t<TR><TD ALIGN="LEFT" PORT="{port_left}">{key}</TD>\n'
          f'\t\t<TD ALIGN="LEFT">{type_}</TD>\n'
          f'\t\t<TD ALIGN="LEFT" PORT="{port_right}">{field}</TD>\n'
          '\t</TR>\n'
        )
      label = label + ('</TABLE>>')
      sub_graph.node(f'{pack_name}_{table_name}',
                     label=label, shape='none')
    full_graph.subgraph(sub_graph)

  # add missing data packages
  for pack_name, package in database.items():
    for table_name, table in package.items():
      for field in table.index:
        if table['foreign'].at[field]:
          edge_direction = table['direction'].at[field]
          parent_pack = table['package'].at[field]
          parent_table = table['table'].at[field]
          parent_field = table['field'].at[field]
          parent_type = table['type'].at[field]

          if parent_pack not in database.keys():
            # sub_graph.node(f'{parent_pack}_other',
            #                label='...', shape='none')
            with full_graph.subgraph(
                name=f'cluster_{pack_name}'
            ) as sub_graph:
              with sub_graph.subgraph(
                  name=f'cluster_{pack_name}_{parent_pack}'
              ) as subsub_graph:
                subsub_graph.graph_attr["style"] = "dashed"
                subsub_graph.graph_attr["label"] = parent_pack

  # add missing tables
  for pack_name, package in database.items():
    for table_name, table in package.items():
      for field in table.index:
        if table['foreign'].at[field]:
          edge_direction = table['direction'].at[field]
          parent_pack = table['package'].at[field]
          parent_table = table['table'].at[field]
          parent_field = table['field'].at[field]
          parent_type = table['type'].at[field]

          if parent_pack not in database.keys():
            label = ('<<TABLE BORDER="0" CELLBORDER="1" '
                     'CELLSPACING="0">\n'
                     '\t<TR><TD ALIGN="LEFT" PORT="pk" COLSPAN="3" ><B>'
                     f'{parent_table}</B> \n\t</TD></TR>\n')
            port_left = parent_field + '_left'
            port_right = parent_field + '_right'
            label = label + (
              f'\t<TR><TD ALIGN="LEFT" PORT="{port_left}">PK</TD>\n'
              f'\t\t<TD ALIGN="LEFT">{parent_type}</TD>\n'
              f'\t\t<TD ALIGN="LEFT" PORT="{port_right}">'
              f'{parent_field}</TD>\n\t</TR>\n'
            )
            label = label + (
              '\t<TR><TD ALIGN="LEFT">...</TD>\n'
              '\t\t<TD ALIGN="LEFT">...</TD>\n'
              '\t\t<TD ALIGN="LEFT">...</TD>\n'
              '\t</TR>\n'
            )
            label = label + ('</TABLE>>')
            with full_graph.subgraph(
                name=f'cluster_{pack_name}'
            ) as subgraph:
              with subgraph.subgraph(
                  name=f'cluster_{pack_name}_{parent_pack}'
              ) as subsubgraph:
                subsubgraph.node(
                  f'{pack_name}_{parent_pack}_{parent_table}',
                  label=label, shape='none')
          else:
            if parent_table not in database[parent_pack].keys():
              label = ('<<TABLE BORDER="0" CELLBORDER="1" '
                       'CELLSPACING="0">\n\t<TR><TD ALIGN="LEFT" '
                       'PORT="pk" COLSPAN="3" ><B>'
                       f'{parent_table}</B> \n\t</TD></TR>\n')
              port_left = parent_field + '_left'
              port_right = parent_field + '_right'
              label = label + (
                f'\t<TR><TD ALIGN="LEFT" PORT="{port_left}">PK</TD>\n'
                f'\t\t<TD ALIGN="LEFT">{parent_type}</TD>\n'
                f'\t\t<TD ALIGN="LEFT" PORT="{port_right}">'
                f'{parent_field}</TD>\n\t</TR>\n'
              )
              label = label + (
                '\t<TR><TD ALIGN="LEFT"></TD>\n'
                '\t\t<TD ALIGN="LEFT">...</TD>\n'
                '\t\t<TD ALIGN="LEFT">...</TD>\n'
                '\t</TR>\n'
              )
              label = label + ('</TABLE>>')
              with full_graph.subgraph(
                  name=f'cluster_{parent_pack}'
              ) as subgraph:
                subgraph.node(f'{parent_pack}_{parent_table}',
                              label=label, shape='none')

  # add foreign key relations
  for pack_name, package in database.items():
    for table_name, table in package.items():
      for field in table.index:
        if table['foreign'].at[field]:
          edge_direction = table['direction'].at[field]
          parent_pack = table['package'].at[field]
          parent_table = table['table'].at[field]
          parent_field = table['field'].at[field]
          parent_type = table['type'].at[field]
          edge_style = table['style'].at[field]

          if parent_pack not in database.keys():
            source_node, target_node = format_external(
              pack_name, table_name, field, parent_pack, parent_table,
              parent_field, edge_direction)
            full_graph.edge(source_node,
                            target_node,
                            dir=edge_direction)
          elif ((parent_table == table_name)
                and (parent_pack == pack_name)):
            source_node, target_node = format_self(
              pack_name, table_name, field, parent_pack, parent_table,
              parent_field, edge_direction)
            full_graph.edge(source_node,
                            target_node,
                            dir=edge_direction,
                            label=' ')
          else:
            source_node, target_node = format_internal(
              pack_name, table_name, field, parent_pack, parent_table,
              parent_field, edge_direction)
            full_graph.edge(source_node,
                            target_node,
                            dir=edge_direction,
                            style=edge_style)

  # full_graph.view()
  full_graph.render(f'{filepath}.gv', view=False, format='svg')

  return full_graph


def format_self(
    pack_name, table_name, field, parent_pack, parent_table,
    parent_field, edge_direction):
  """Format foreign key relation with same table."""
  if edge_direction == 'forward':
    target_node = f'{pack_name}_{table_name}:{field}_left:w'
    source_node = (f'{parent_pack}_{parent_table}:'
                   f'{parent_field}_left:w')
  elif edge_direction == 'back':
    source_node = f'{pack_name}_{table_name}:{field}_left:w'
    target_node = (f'{parent_pack}_{parent_table}:'
                   f'{parent_field}_left:w')
  else:
    raise KeyError('direction mandatory: forward or back')
  return source_node, target_node


def format_internal(
    pack_name, table_name, field, parent_pack, parent_table,
    parent_field, edge_direction):
  """Format foreign key relation with table in same data package."""
  if edge_direction == 'forward':
    target_node = f'{pack_name}_{table_name}:{field}_left'
    source_node = (f'{parent_pack}_{parent_table}:'
                   f'{parent_field}_right')
  elif edge_direction == 'back':
    source_node = f'{pack_name}_{table_name}:{field}_right'
    target_node = (f'{parent_pack}_{parent_table}:'
                   '{parent_field}_left')
  else:
    logger.error('direction mandatory: forward or back')
    raise KeyError
  return source_node, target_node


def format_external(
    pack_name, table_name, field, parent_pack, parent_table,
    parent_field, edge_direction):
  """Format foreign key relation with table in another data package."""
  if edge_direction == 'forward':
    target_node = f'{pack_name}_{table_name}:{field}_left'
    source_node = (f'{pack_name}_{parent_pack}_{parent_table}:'
                   f'{parent_field}_right')
  elif edge_direction == 'back':
    source_node = f'{pack_name}_{table_name}:{field}_right'
    target_node = (f'{pack_name}_{parent_pack}_{parent_table}:'
                   '{parent_field}_left')
  else:
    logger.error('direction mandatory: forward or back')
    raise KeyError
  return source_node, target_node
