import contextlib
import inspect
import logging
import os
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Union

import pandas as pd


class Resource:
    def __init__(
        self,
        name: str | None = None,
        loc: Union[Path, str] = None,
        task_name: str = None,
        task_relation: str = None,
        last_update: date = date.today(),
        comment: str = None,
    ) -> None:
        self.name = name
        self.loc = self._parse_loc(loc)
        self.task_name = task_name
        self.task_relation = task_relation
        self.last_update = last_update
        self.comment = comment
        assert self.task_name is not None, "task_name is not set"
        assert self.loc is not None, "loc is not set correctly"
        assert not Path(
            self.loc
        ).is_absolute(), "loc should be a path relative to BONSAI_HOME"

        if not self.name:
            self._parse_name_from_loc()
        assert isinstance(self.loc, str) and isinstance(
            self.name, str
        ), "The loc or name attribute of the resource is not set correctly"

    @staticmethod
    def _parse_loc(loc: Union[Path, str]) -> str:
        assert loc is not None, "loc should not be None"
        bonsai_home = Path(os.getenv("BONSAI_HOME", None))
        assert bonsai_home, EnvironmentError(
            "BONSAI_HOME environmental varaible is not set"
        )

        if isinstance(loc, Path):
            # Check if loc is an absolute path
            if loc.is_absolute():
                # Make loc relative to BONSAI_HOME
                try:
                    loc_formatted = str(loc.relative_to(bonsai_home))
                except ValueError:
                    # loc_path is not a subpath of BONSAI_HOME; handle as needed
                    raise ValueError(
                        f"Provided path {loc} is not within BONSAI_HOME {bonsai_home}"
                    )
            else:
                loc_formatted = str(loc)
        else:
            loc_formatted = loc
        return loc_formatted

    def _parse_name_from_loc(self):
        if "http" in str(self.loc):
            self._parse_url()
        else:
            self._parse_path()

    def _parse_url(self):
        import urllib

        parsed_source = urllib.parse.urlparse(self.loc)
        ls_path_name = parsed_source.path.split("/")
        self.name = ls_path_name[-1] if ls_path_name[-1] else ls_path_name[-2]

    def _parse_path(self):
        self.name = Path(self.loc).name

    def to_dataframe(self, **kwargs) -> pd.DataFrame:
        from dataio.utils.hsut.io import DataReader

        if self.loc.startswith("http"):
            # If self.loc is an API endpoint, use it directly
            return DataReader(self.loc).read(**kwargs)
        else:
            # Assume self.loc is a relative path, construct the full path
            bonsai_home = Path(os.getenv("BONSAI_HOME", ""))
            assert bonsai_home, EnvironmentError(
                "BONSAI_HOME environmental variable is not set"
            )

            full_path = bonsai_home / self.loc
            return DataReader(full_path).read(**kwargs)

    @classmethod
    def from_dataframe(
        cls,
        data: pd.DataFrame,
        loc: Union[Path, str],
        task_name: str,
        task_relation: str,
        last_update: date = date.today(),
        comment: str = None,
        **kwargs,
    ) -> "Resource":
        from dataio.utils.hsut.io import DataWriter

        if isinstance(loc, Path):
            if not loc.is_absolute():

                bonsai_home = Path(os.getenv("BONSAI_HOME", None))
                assert EnvironmentError(
                    "<BONSAI_HOME> environment variable is not set."
                )
                loc = bonsai_home / loc
        DataWriter(loc).write(data, **kwargs)
        res = Resource(
            loc=loc,
            task_name=task_name,
            task_relation=task_relation,
            last_update=last_update,
            comment=comment,
        )
        # res.append_comment(comment)
        return res

    def append_comment(self, comment: str):
        if self.comment is not None and comment in self.comment:
            logging.warning(
                f"""Comment ignored! 
                The added comment `{comment}` is already in the comment field. No need to add again.
                Please check the comment of the resource {self.name}"""
            )
        elif self.comment is None:
            self.comment = comment
        else:
            self.comment = self.comment + "\n" + comment


class ResourceRepository(ABC):
    @abstractmethod
    def add_or_update(self, resource: Resource):
        raise NotImplementedError

    @abstractmethod
    def add(self, resource: Resource):
        raise NotImplementedError

    @abstractmethod
    def update(self, resource: Resource):
        raise NotImplementedError

    @abstractmethod
    def get(self, **filters) -> Resource:
        raise NotImplementedError

    @abstractmethod
    def get_dataframe_for_task(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Resource]:
        raise NotImplementedError


class CSVResourceRepository(ResourceRepository):
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.table_name = "resources"
        self.csv_path = self.db_path / (self.table_name + ".csv")
        self.df_columns = [
            "name",
            "loc",
            "task_name",
            "task_relation",
            "last_update",
            "comment",
        ]

        # Initialize CSV file if it does not exist
        if not self.csv_path.exists():
            pd.DataFrame(columns=self.df_columns).to_csv(self.csv_path, index=False)
        self.df = pd.read_csv(self.csv_path)
        # self.df["loc"] = self.df["loc"].apply(lambda x: Path(x))

    def add_or_update(self, resource: Resource, **kwargs) -> None:

        # Check if the resource exists
        exists = (
            (self.df["name"] == resource.name)
            & (self.df["task_name"] == resource.task_name)
            & (self.df["task_relation"] == resource.task_relation)
        ).any()

        if exists:
            self.update(resource)
        else:
            self.add(resource)

    def add(self, resource: Resource) -> None:
        # Append new record
        new_record = pd.DataFrame(
            [
                [
                    resource.name,
                    resource.loc,
                    resource.task_name,
                    resource.task_relation,
                    resource.last_update,
                    resource.comment,
                ]
            ],
            columns=self.df_columns,
        )
        self.df = pd.concat([self.df, new_record], ignore_index=True)
        self.df.to_csv(self.csv_path, index=False)

    def update(self, resource: Resource) -> None:
        # Update existing record
        self.df.loc[
            (self.df["name"] == resource.name)
            & (self.df["task_name"] == resource.task_name)
            & (self.df["task_relation"] == resource.task_relation),
            ["loc", "last_update", "comment"],
        ] = [resource.loc, resource.last_update, resource.comment]
        self.df.to_csv(self.csv_path, index=False)

    def get(self, **filters: dict) -> Resource:
        mask = pd.Series(True, index=self.df.index)

        for k, v in filters.items():
            # Update the mask to narrow down the rows
            mask = mask & (self.df[k] == v)
        result = self.df[mask]
        # query = " & ".join([f"{k}=='{v}'" for k, v in filters.items()])
        # result = self.df.query(query)
        if result.empty:
            raise ValueError(f"No resource found with the provided filters: {filters}")
        row = result.iloc[0]
        return Resource(
            name=row["name"],
            loc=row["loc"],
            task_name=row["task_name"],
            task_relation=row["task_relation"],
            last_update=row["last_update"],
            comment=row["comment"],
        )

    def add_from_dataframe(
        self,
        data: pd.DataFrame,
        loc: Union[Path, str],
        task_name: str | None = None,
        task_relation: str = "output",
        last_update: date = date.today(),
        **kwargs,
    ) -> Resource:
        res = Resource.from_dataframe(
            data,
            loc,
            task_name,
            task_relation=task_relation,
            last_update=last_update,
            **kwargs,
        )
        self.add_or_update(res)
        return res

    def get_dataframe_for_task(
        self,
        name: str = None,
        loc: Path = None,
        task_name: str = None,
        task_relation="input",
        **kwargs,
    ) -> pd.DataFrame:

        if task_name is None:
            # Get the call stack
            stack = inspect.stack()

            # Find `get_dataframe_for_task` in the call stack
            for i, frame in enumerate(stack):
                if frame.function == "get_dataframe_for_task":
                    # Use the function above `get_dataframe_for_task` in the stack
                    if i + 1 < len(stack):
                        task_name = stack[i + 1].function
                    else:
                        raise RuntimeError(
                            "Caller function for `get_dataframe_for_task` not found."
                        )
                    break
            if not any([name, loc]):
                raise ValueError("name or loc must be specified to get a dataframe")

        res = Resource(
            name=name, loc=loc, task_name=task_name, task_relation=task_relation
        )
        try:
            filters = {}
            for k, v in zip(
                ["name", "loc", "task_name", "task_relation"],
                [res.name, res.loc, res.task_name, res.task_relation],
            ):
                if v is not None:
                    filters[k] = v
            res = self.get(**filters)
        except ValueError:
            res_identifier = f"{res.name}@{res.loc}"
            print(
                f"The required resource {res_identifier} is not registered before. Start to register the resource"
            )
            self.add_or_update(res)
        res.last_update = date.today()
        return res.to_dataframe(**kwargs)

    def list(self) -> list[Resource]:

        resources = [
            Resource(
                name=row["name"],
                loc=row["loc"],
                task_name=row["task_name"],
                task_relation=row["task_relation"],
                last_update=pd.to_datetime(row["last_update"]).date(),
                comment=row["comment"],
            )
            for index, row in self.df.iterrows()
        ]
        return resources

    def comment_res(self, resource: Resource, comment: str) -> Resource:
        resource.append_comment(comment)
        self.add_or_update(resource)
        return resource


class SQLiteResourceRepository(ResourceRepository):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path / "database.db"

        self.table_name = "resources"
        self._init_db()

    @contextlib.contextmanager
    def connect(self):
        import sqlite3

        with sqlite3.connect(self.db_path) as conn:
            yield conn.cursor()

    def _init_db(self):
        with self.connect() as cursor:
            cursor.execute(
                f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (name TEXT, loc TEXT, task_name TEXT, task_relation TEXT, last_update DATE, comment TEXT)
"""
            )

    def add(self, resource: Resource, **kwargs):
        with self.connect() as cursor:
            cursor.execute(
                f"""
INSERT INTO {self.table_name} (name, loc, task_name, task_relation, last_update, comment) VALUES (?, ?, ?, ?, ?, ?)
""",
                (
                    resource.name,
                    resource.loc,
                    resource.task_name,
                    resource.task_relation,
                    resource.last_update,
                    resource.comment,
                ),
            )
            return resource

    def update(self, resource: Resource, **kwargs):
        with self.connect() as cursor:
            cursor.execute(
                f"""
    UPDATE {self.table_name} SET loc=?, last_update=? WHERE name=? AND task_name=? AND task_relation=?
    """,
                (
                    resource.loc,
                    resource.last_update,
                    resource.name,
                    resource.task_name,
                    resource.task_relation,
                ),
            )

    def add_or_update(self, resource: Resource, **kwargs) -> None:
        with self.connect() as cursor:
            cursor.execute(
                f"""
SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE name=? AND task_name=? AND task_relation=? LIMIT 1)
""",
                (
                    resource.name,
                    resource.task_name,
                    resource.task_relation,
                ),
            )
            exists = cursor.fetchone()[0]
            if exists:
                self.update(resource)
            else:
                self.add(resource)

    def add_from_dataframe(
        self,
        data: pd.DataFrame,
        loc: Union[Path, str],
        task_name: str | None = None,
        task_relation: str = "output",
        last_update: date = date.today(),
        **kwargs,
    ) -> None:
        res = Resource.from_dataframe(
            data,
            loc,
            task_name,
            task_relation=task_relation,
            last_update=last_update,
            **kwargs,
        )
        self.add_or_update(res)

    def get(self, **filters: dict) -> Resource:
        assert (
            "name" in filters.keys() or "loc" in filters.keys()
        ), "Must provide at least name or loc as a filter"
        query_columns = ["name", "loc", "task_name", "task_relation"]
        query = f"SELECT {', '.join(query_columns)} FROM {self.table_name} WHERE "

        conditions = []
        parameters = []
        for column, value in filters.items():
            if value is None:
                continue
            if column in query_columns:
                conditions.append(f"{column} = ?")
                parameters.append(value)

        if not conditions:
            raise ValueError("At least one valid filter must be provided.")

        query += " AND ".join(conditions)

        with self.connect() as cursor:
            cursor.execute(
                query,
                tuple(parameters),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(
                    f"No resource found with the provided filters: {filters}"
                )
            res = Resource(
                name=row[0], loc=row[1], task_name=row[2], task_relation=row[3]
            )
            return res

    def get_dataframe_for_task(
        self,
        name: str = None,
        loc: Path = None,
        task_name: str = None,
        task_relation="input",
        **kwargs,
    ) -> pd.DataFrame:
        if not any([name, loc]):
            raise ValueError("name or loc must be specified to get a dataframe")
        if loc:
            loc = Resource._parse_loc(loc=loc)
        res = Resource(
            name=name, loc=loc, task_name=task_name, task_relation=task_relation
        )
        try:
            res = self.get(name=name, loc=loc, task_name=task_name)
        except ValueError:
            print(
                f"Resource {res.name} is not registered before. Start to register the resource"
            )
            self.add_or_update(res)
        res.last_update = date.today()
        return res.to_dataframe(**kwargs)

    def list(self) -> list[Resource]:
        with self.connect() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM {self.table_name}
                """
            )
            rows = cursor.fetchall()
            return [
                Resource(
                    name=row[0],
                    loc=row[1],
                    task_name=row[3],
                    task_relation=row[4],
                    comment=row[5],
                )
                for row in rows
            ]

    def to_csv(self, path: Union[Path, str]) -> None:
        import csv

        with self.connect() as cursor, open(path, "w", newline="") as file:
            writer = csv.writer(file)
            # Writing the header
            writer.writerow(
                [
                    "name",
                    "location",
                    "task_name",
                    "task_relation",
                    "last_update",
                    "comment",
                ]
            )
            cursor.execute(
                "SELECT name, loc, task_name, task_relation, last_update, comment FROM resources"
            )
            for row in cursor.fetchall():
                writer.writerow(row)
