# Changelog
## 4.8.17
- Splits the comtradeservices external schema into two due to classification issues.

## 4.8.16
- Add external schema for USA MSUTs: USAMonetarySUT
- Fix logger messages
- Update convert_units, remove convert_units_pandas (obsolete)
- add schemas for simplified ppf

## 4.8.15
- implements the pint unit registry from classifications to do the unit conversion.

## 4.8.14
- added flowobject correspondence to ComtradeServices

## 4.8.13
- bugfix ComtradeServices

## 4.8.12
- bugfix ComtradeServices

## 4.8.11
- added ComtradeServices


## 4.8.10
- fixed optionals OECDWaste, ExternalWaste and EurostatWaste

## 4.8.9
- added OECDWaste and EurostatWaste

## 4.8.8
- added PopulationData

## 4.8.7
- added some more robustness to how dataio and resource.csv interacts

## 4.8.6
- add external schema ExternalWaste and update  statcan for pairwise product and activity
- remove reload_if_stale and add more instances of reloading resource.csv
- updated _reload_resources_csv to be able to handle dicts

## 4.8.5
- Update config to match hybrid_sut config

## 4.8.4
- Hotfix: updated PathBuilder init in Config

## 4.8.3
- Hotfix: fixed BACI schema for location

## 4.8.2
- Updated Config to stay compatible with hybrid_sut

## 4.8.1
- Fixing concordance pair classification not working
- Reloading resources csv automatically before writing to it to avoid race conditions

## 4.8.0
- Removed coco from dependencies and changed to rely on own classification for location
- Added append parameter in save.py
- Added run_by_user to dataresouce and config.
- Added functionality to check timestamp of resource.csv and if 3 hours old we reload

## 4.7.9
- Hotfix: Updating group_and_sum and summed_df  -> data and remove field_validator for DimensionModel

## 4.7.8
- Hotfix: DataResource was still using BONSAI_HOME -> using DATAIO_ROOT

## 4.7.7
- Hotfix for BACITrade product int -> str

## 4.7.6
- hotfix for an error in group_and_sum method that caused a ValueError

## 4.7.5
- Expose airflow config via static method in Config class
- Performance update for conversion of units, currencies and location

## 4.7.4
- Update external schemas for BACI and ADB
- Add external schema for IO tables from ADB


## 4.7.3
- Changed to_dataclass from iterrows to TypeAdapter.
- fixed merged error in config and added load_env again.
- fixed classifications dicts in internal schemas

## 4.7.2
- Reverted product_code -> product in external monetary schemas classifications.

## 4.7.1
- Updated `StatCanChemProductionVolume`  external schema - added product correspondence

## 4.7.0
- Deprecated CSVResourceRepository please use ResourceRepository instead
- Updated README
- Introduced option for storing data directly in the database via the API
- Update schema for EuropeanMonetarySUT, to point to the correct classification
- Add external schema for African SUTs (ASUT)

## 4.6.4
- updated external schemas classification naming and IndustrialCommodityStatistic location to short_name

## 4.6.3
- removed monetary_value and monetary_unit from trade and production_volumes
- add optional source to both production volumes and trades

## 4.6.2
- added optional accounttype column to use, supply, productionvolumes and trade schemas

## 4.6.1
- Added the UnfcccProductionVolume external schema

## 4.6.0
- Added config from hybrid_sut to make integration smoother

## 4.5.15
- added diagonal to the external SUT schemas
- added the prodcom trade external schema

## 4.5.14
- undo changes on the schema of `Emissions_samples` and `Emissions_uncertainty`

## 4.5.13
- added external schema UNdataWDI
- revised pairwise concordance loading
- added diagonal to the external SUT schemas
- added the prodcom trade external schema
- added a new schema "ContentData"

## 4.5.12
- add transfer_type to transferCoefficients
- handle import_location and export_location as locations
- add classification to trade external schemas for locations
- add convert_dataframe ability to handle trade locations

## 4.5.11
- Correction of FAOSTAT dat schema (for classification)

## 4.5.10
- Modified external schemas for PRODCOM location codes: GEOnumeric

## 4.5.9
- Fixed tests for new version of classification package
- Fixed units not being parameter of `load_with_classification`
- Handle one-to-many correspondences in generate_classification_mapping()
- fixed `load_table_file()` not working with `samples` columns

## 4.5.8
- Modified external schema field: final_user

## 4.5.7
- added monetary fields to production volume and trade
- added api_endpoint and removed description from dataResource

## 4.5.6
- Added external schemas for FAOstat data: FAOstat and FAOtrade

## 4.5.5
- added external schema comext

## 4.5.4
- added external schema StatCanChemProductionVolume
- added location to USGS external schema

## 4.5.3
- added `resource_repository.get_dataframe_for_resource(self, resource: DataResource)`

## version 4.5.2
-  resource now inherits from emissions and added elementary type

## version 4.5.1
-  Add a new category of schemas that include the sample vector. All the old schemas have been renamed to 'oldname_uncertainty' and all the new schemas are called 'oldname_samples'

## 4.5.0
- added functionality to allow dataio do deal with concordance pair matrices
- added unit conversion. You now have the possibility to use the following APIs to convert units
  - pass a "units" list with the set of target units to the `load_with_classification` e.g. `["tonne", "km", "EUR"]`
  - directly use `resource_repository.convert_units(data: pd.DataFrame, target_units: list[str])`
  - use the `resource_repository.valid_units()` to get a list of available units

## 4.4.1
- fixed `get_empty_dataframe()` not providing correct dtypes

## 4.4.0
- reworked classification converting and introduced a new API `convert_dataframe` and `convert_dataframe_to_bonsai_classification` that can be used to directly convert a dataframe without having to use the load method.

## version 4.3.3
- New external schemas for SUTs, inheriting from ExternalMonetarySUT
- New internal schemas for components of SUTs

## 4.3.2
- renamed classification for USGSProductionVolume schema

## 4.3.1
- fixed bug with windows paths not being interpreted correctly

## 4.3.0
- load_with_classification and load_with_bonsai_classification now have a new way of interacting

## version 4.2.0
- load_with_classifications now allows lists in the dict values which allows multiple classifications of same column in a single call.

## version 4.1.3
- Removed quantity from the trade schema

## version 4.1.2
- fixed self.available_resources is a now not a dict but an empty dataframe when freshly initialized

## version 4.1.1
- updated classifications requirements in setup.cfg

## version 4.1.0
- added load_with_classification and load_with_bonsai_classification methods to csvrepository along with tests.
- added transform_dataframe method to BonsaiBaseModel.
- added harmonize_with_resource to csvrepository
- added many smaller helper methods for these

## version 4.0.6
- NA in input files is no longer detected as NaN value. Full list of currently detected NaN values:
  ["", "NaN", "N/A", "n/a", "nan"]

## version 4.0.5
- Fixed deprecation warnings for pydantic
- Added minimum required version for pydantic to avoid install-errors

## version 4.0.4
-Bugfix ExternalDimensionTables inheritance.

## version 4.0.3
-Bugfix init import * schemas

## version 4.0.2
-Added PropertyOfProducts schema
-Added associated_product to use and supply.
-Confirmed trade is the correct schema
-Added product destination to supply
-Added ExternalDimensionTables

## version 4.0.1
- Added BrokenYearMonetarySUT as external schema which is used for specific type of monetary SUT, for tables with annual data that start on a day other than January 1st. For example for the fiscal year of India.

## version 4.0.0
- added B_Matrix schema to MatrixModel
- updated PPF-fact-schema with units for activities and products

## version 3.3.0
- BREAKING CHANGE: current task name is now required by Config!
- added/updated arg_parser and set_logger from utilities
- fixed bug with loading csv not interpreting nan values correctly
- fixed bug with loading csv didn't parse bool values correctly

## version 3.2.0
- Added feature to save matrices, by specifying the datatype to be .h5 in the location field of a resource
- Also added MatrixModels to schema
  - A_Matrix
  - Inverse
  - IntensitiesMatrix

## version 3.1.7
- Added external schema USGSProductionVolume

## version 3.1.6
- Fixed bug where last_update column to resources.csv was not saved and loaded in iso format

## version 3.1.5
- Fixed bug when only single resource was loaded with get_resource_info

## version 3.1.4
- Added external schemas for: external monetary SUT, PRODCOM production volumes, UN and BACI data

## version 3.1.3
- Bugfix that ensures that the resource name and the file name does not need to be identical

## version 3.1.2
- added schemes for classifications
- revisions of names for schemes to synchronize with Bonsai ontology

## version 3.1.1
- changed behaviour of DataResource location. It is now possible to specify a root_location that is used to create absolute paths from relative locations.
- with this change, location in resources.csv for CSVResourceRepository are now all relative to the resources.csv file!

## version 3.1.0
- feature change: load and all dependent methods now return a dict if more than one file is loaded, otherwise returns just a dataframe.

##  version 3.0.4
- bug fix -> uncertainty columns from get_empty_dataframe not double anymore

## version 3.0.3
- bug fix -> location now stored in relative format
- bug fix -> updating resource now works as expected
- resource_exists function now only works with non-metadata information (e.g. comment field is ignored when checking)

## version 3.0.2 (resource_exists)

- bug fixes
- added resource_repository.resource_exists(resource) -> bool.

## version 3.0.1 (flexible location)

- bug fixes
- added the possibility to use variables in the location name (e.g. `clean/production/{version}/industry.csv`) is now possible.

## version 3.0.0 (rework of dataio)

This version potentially breaks old code that relies on the dataio package.

- **CSV Resource Repository**: Introduced a new `CSVResourceRepository` class to manage data resources stored in CSV files, enabling adding, updating, and listing of resources.
- **Data Validation**: Implemented data validation methods that ensure the integrity of data before it is saved, aligning with predefined schemas.
- **Environment Setup**: Added functionality to set the `BONSAI_HOME` environment variable for specifying the project's home directory.
- **Resource Manipulation Methods**: New methods for adding, updating, and retrieving data resources, including:
  - `add_to_resource_list`
  - `update_resource_list`
  - `get_resource_info`
- **Data Handling Methods**: Developed methods to read and write DataFrame objects directly related to specific tasks and resources, enhancing ease of data manipulation:
  - `write_dataframe_for_task`
  - `get_dataframe_for_task`
- **Test Suite**: A comprehensive test suite has been added to ensure the reliability and performance of the new functionalities.
- **Documentation**: Provided detailed README.md documentation to assist users in understanding and utilizing the new features effectively.


## Version 2.0.3 (fixed bugs)

- read csv files into pandas dataframe properly (e.g. avoid converting `NA` into NaN)
- raise Error when `frictionless.validate` fails


## Version 2.0.2 (minor changes)

- added future work
- changed tox.ini


## Version 2.0.1 (included datapackage dependencies)

- edited validate to check foreign keys to field datapackages in metadata
- implemented dialect handling (delimiter, quotation character and skipinitialvalue)
- edited docs (syntax, future developments, tutorials)
- updated tutorials
- improved user experience (renamed validate report, provided plot output options)


## Version 1.2.7 (small fix)

- create/dump renaming bug
- Layout of create docstring is not good


## Version 1.2.6 (fixed log refs)

- Older terms like dump and visualize were fixed to save and plot


## Version 1.2.5 (log path of saved metadata and tables)

- changed log strings


## Version 1.2.4 (fixed datapackage save index issues)

- 'id' is index, now column exported with proper name


## Version 1.2.3 (fixed datapackage create docstring)

- Concerning tables


## Version 1.2.1 (fixed bug in datapackage create function)

- Indent was misplaced


## Version 1.2.0 (revised tutorials and added metadata syntax)

- Additionaly revised terminology and simplified API of several functions


## Version 1.1.0 (added features to 'dump' and 'describe')

- Added instructions on use of help() and dir() to 'load' toy model
- Added auto-increment option to 'dump'
- Added option to override metadata fields to 'describe'


## Version 1.0.7 (improved user-friendliness)

- Changed version dependency of pandas in setup.cfg install_requires from >= to None
- Changed validate to raise exception only after running all pre-frictionless tests
- Changed describe to accept absolute paths
- Changed all functions to allow both Path and string paths
- Removed output of <name>.datapackage.yaml from describe


## Version 1.0.6 (made dependencies flexible)

- Changed version dependencies in setup.cfg install_requires from == to >=


## Version 1.0.5 (fixed web documentation)

- Renamed subfolder with datapackage
- Reformatted docstrings


## Version 1.0.4 (generate latex documentation)

- Edited several configuration files


## Version 1.0.3 (added jupyter notebooks)

- Added jupyter notebooks to load and dump tutorials
- Added print statements to load and dump tutorials
- Renamed distro to match package name to fix website version number issue


## Version 1.0.2 (fixed instructions)

- Fixed instructions for installing package
- BUG: API is not rendering in website
- BUG: website is showing unknown version


## Version 1.0.0 (datapackage is working)

- Functions describe, validate, visualize, load, dump working for datapackage
- Tests using export illustrations working


