from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List

import pandas as pd


class IncompleteDatapackageException(Exception):
    pass


@dataclass
class Author:
    name: str
    affiliation: str
    e_mail: str


@dataclass
class Algorithm:
    name: str
    version_number: str


@dataclass
class ModifiedBy:
    authors: List[Author]
    algorithm: Algorithm


@dataclass
class License:
    acronym: str
    full_name: str
    description: str
    link: str


@dataclass
class Source:
    reference: str
    encoding: str
    link: str
    authors: List[str]
    institution: str
    type: str
    license: License
    language: str
    link_doc: str = ""


@dataclass
class Field:
    name: str
    foreign_name: str = ""
    resource: str = ""
    external_path: str = ""


class BaseTable:
    def __init__(self, data=None, fields=None):
        self.data = data
        self.fields = fields

    def __repr__(self):
        return str(self.data)

    def assert_completeness(self):
        all_indicies = self.data.columns.to_list() + self.data.index.names

        for i in all_indicies:
            if i not in self.fields:
                raise IncompleteDatapackageException(f"Field {i} missing")

    def to_csv(self, path):
        self.data.to_csv(path)

    @classmethod
    def from_json(cls, json_string, field_metadata):
        data = pd.DataFrame(json_string)

        # convert decimal columns to float
        dec_data = data.convert_dtypes().select_dtypes("object")
        if not dec_data.empty:
            data[dec_data.columns] = dec_data.astype(float)

        columns = data.columns.to_list().copy()

        fields = {}
        if field_metadata:
            for field in field_metadata:
                name = field["fields"][0]
                columns.remove(name)
                fields[name] = Field(
                    name,
                    foreign_name=field["reference"]["fields"][0],
                    resource=field["reference"]["resource"],
                )

                if "external_path" in field["reference"]:
                    fields[name].external_path = field["reference"]["external_path"]

        for remaining_name in columns:
            fields[remaining_name] = Field(remaining_name)

        return BaseTable(data, fields)


class FactTable(BaseTable):
    type = "fact"

    def __init__(self, data: pd.DataFrame, fields: Dict[str, Field]):
        super().__init__(data, fields)

    def __eq__(self, table):
        if not self.data.equals(table.data):
            return False
        return True

    @classmethod
    def from_json(cls, json_string, field_metadata, value_field="value"):

        table = super().from_json(json_string, field_metadata)

        ind_list = table.data.columns.to_list()
        ind_list.remove(value_field)
        data = table.data.set_index(ind_list)

        return FactTable(data, table.fields)


class AttributeTable(BaseTable):
    type = "attribute"

    def __init__(
        self, data: pd.DataFrame, fields: Dict[str, Field], name: str, category: str
    ):
        super().__init__(data, fields)
        self.name = name
        self.category = category

    def __eq__(self, table):
        if self.name != table.name:
            return False
        if self.category != table.category:
            return False
        if not self.data.equals(table.data):
            return False
        return True

    @classmethod
    def from_json(cls, json_string, field_metadata, name: str, category: str):
        table = super().from_json(json_string, field_metadata)

        data = table.data.set_index("code")

        return AttributeTable(data, table.fields, name, category)


class DataPackage:
    """
    This class provides data for loading and saving data for the GTDR project.
    It is designed so that it can provide information for both storage on fileshare
    as well as in a potiential future database.

    Data itself is stored in a pandas DataFrame. The descriptors of the different
    dimensions is stored in a dictionary with DataDescription objects as values
    and the name of the corresponding index in the pandas DataFrame as key.

    -------------
    Example:
    --
    pd.DataFrame with MultiIndex:
    region: [1, 2, 3, 2, 1, 2]
    industry: [2, 3, 4, 5, 6, 7]

    data: [0.1, 2.3, 5.3, 2.33, 23.2, 0.02]
    --
    DataDescriptions:
    {
        "region": DataDescription object,
        "industry": DataDescription object
    }
    -------------
    """

    def __init__(
        self,
        name: str,
        category_path: str,
        version: str,
        title=None,
        comment=None,
        tables=defaultdict(lambda: BaseTable()),
        source=None,
        modified_by=None,
        last_modified=None,
        target_language=None,
        encoding=None,
    ):
        """
        Parameters
        -------------
        data:

        """
        self.name = name
        self.category_path = category_path
        self.version = version

        self.title = title
        self.comment = comment

        self.tables = tables

        self.source = source
        self.modified_by = modified_by
        self.last_modified = last_modified
        self.target_language = target_language
        self.encoding = encoding

    @property
    def tables(self):
        return self._tables

    @tables.setter
    def tables(self, tables):
        self._tables = tables
        # make it possible to include tables
        for name, table in self.tables.items():
            setattr(self, name, table)

    def get_full_data(self):
        """
        This method returns a pandas DataFrame where the numerical values for the
        data descriptiors are replaced by their proper name
        """

        pass

    def __str__(self) -> str:
        returnstr = ""
        for name, table in self.tables.items():
            returnstr += f"{name}\n{table.data}\n\n"
        return returnstr

    def __repr__(self) -> str:
        returnstr = ""
        for name, table in self.tables.items():
            returnstr += f"{name}\n{table.data}\n\n"
        return returnstr

    def __eq__(self, datapackage):
        if self.name != datapackage.name:
            return False
        if self.category_path != datapackage.category_path:
            return False
        if self.version != datapackage.version:
            return False
        if self.title != datapackage.title:
            return False
        if self.comment != datapackage.comment:
            return False
        if self.source != datapackage.source:
            return False
        if self.modified_by != datapackage.modified_by:
            return False
        if self.last_modified != datapackage.last_modified:
            return False
        if self.target_language != datapackage.target_language:
            return False
        if self.encoding != datapackage.encoding:
            return False

        if self.tables.keys() != datapackage.tables.keys():
            return False
        for name, table in self.tables.items():
            if table != datapackage.tables[name]:
                return False

        return True

    def assert_completeness(self):
        """
        Checks if the required fields in the DataPackage instance are present.
        Raises IncompleteDatapackageException if a required field is missing.
        """
        if not self.name:
            raise IncompleteDatapackageException("DataPackage name field missing")

        if not self.source:
            raise IncompleteDatapackageException("DataPackage source field missing")

        if not self.modified_by:
            raise IncompleteDatapackageException(
                "DataPackage modified_by field missing"
            )

        if not self.target_language:
            raise IncompleteDatapackageException(
                "DataPackage target_language field missing"
            )

        for table in self.tables.values():
            table.assert_completeness()


class Database:
    def __init__(self, datapackages: Dict[str, DataPackage]):
        self.datapackages = datapackages

    @property
    def datapackages(self):
        return self._datapackages

    @datapackages.setter
    def datapackages(self, datapackages):
        self._datapackages = datapackages

        for name, datapackage in datapackages.items():
            setattr(self, name, datapackage)
