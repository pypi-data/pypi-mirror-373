import inspect
import logging
import os
from datetime import datetime
from pathlib import Path, PurePath, PureWindowsPath
from typing import Optional, Union
from uuid import UUID

import pandas as pd
from pydantic import ConfigDict, Field, computed_field

from dataio.tools import BonsaiBaseModel


class DataResource(BonsaiBaseModel):
    # model_config = ConfigDict(populate_by_name=True)

    id: UUID | None = None  # Only used for api
    run_by_user: str | None = None
    name: str
    schema_name: str
    task_name: str | None = None
    stage: str | None = None
    data_flow_direction: str | None = None
    data_version: str | None = None
    code_version: str | None = None
    comment: str | None = None
    last_update: datetime = Field(default_factory=datetime.now)
    created_by: str | None = None  # Assuming a ForeignKey-like relationship
    license: str | None = None
    license_url: str | None = None
    dag_run_id: str | None = None
    url: str | None = None
    _location: str = "{stage}/{task_name}/{version}/{resource_name}.csv"
    _root_location: str | None = None
    api_endpoint: str | None = None

    @computed_field
    @property
    def location(self) -> str:
        location = self._replace_variables_in_location_string(
            self._location,
            self.name,
            self.task_name,
            self.stage,
            self.data_version,
            self.code_version,
        )
        return self._parse_location(location, self._root_location)

    @location.setter
    def location(self, value: str | PurePath):
        if isinstance(value, str):
            if not value.startswith("http"):
                value = PureWindowsPath(value).as_posix()
        else:
            value = value.as_posix()
        self._location = value

    def __str__(self) -> str:
        return self.name

    def __init__(
        self,
        name: str,
        schema_name: str | BonsaiBaseModel,
        location: str | Path | None = None,
        task_name: str | None = None,
        stage: str | None = None,
        data_flow_direction: str | None = None,
        data_version: str | float | None = None,
        code_version: str | float | None = None,
        comment: str | None = None,
        last_update: datetime | None = None,
        created_by: str | None = None,  # Assuming a ForeignKey-like relationship
        license: str | None = None,
        license_url: str | None = None,
        dag_run_id: str | None = None,
        url: str | None = None,
        root_location: str | Path | None = None,
        api_endpoint: str | None = None,
        id: Optional[UUID] = None,
        run_by_user: str | None = None,
    ) -> None:
        # TODO potentially also allow to automatically generate api endpoint

        if inspect.isclass(schema_name):
            schema_name = schema_name.__name__

        # Dictionary to hold arguments that are not None
        init_args = {"name": name, "schema_name": schema_name}

        # Optional parameters are added only if they are not None
        if isinstance(id, str) and not id:
            # If id is an empty string, treat it as None
            id = None
        if id is not None:
            init_args["id"] = id
        if task_name is not None:
            init_args["task_name"] = task_name
        if stage is not None:
            init_args["stage"] = stage
        if data_flow_direction is not None:
            init_args["data_flow_direction"] = data_flow_direction
        if data_version is not None:
            init_args["data_version"] = data_version
        if code_version is not None:
            init_args["code_version"] = code_version
        if comment is not None:
            init_args["comment"] = comment
        if last_update is not None:
            init_args["last_update"] = last_update
        if created_by is not None:
            init_args["created_by"] = created_by
        if license is not None:
            init_args["license"] = license
        if license_url is not None:
            init_args["license_url"] = license_url
        if url is not None:
            init_args["url"] = url
        if api_endpoint is not None:
            init_args["api_endpoint"] = api_endpoint
        if isinstance(run_by_user, str) and not run_by_user:
            # If id is an empty string, treat it as None
            run_by_user = None
        if run_by_user is not None:
            init_args["run_by_user"] = run_by_user

        # Call to the superclass constructor with filtered parameters
        super().__init__(**init_args)

        # making sure that all paths are always handled as posixpaths
        if location is not None:
            self.location = location

        if root_location:
            if isinstance(root_location, str):
                if root_location.startswith("http"):
                    self._root_location = root_location
                else:
                    self._root_location = PureWindowsPath(root_location).as_posix()
            else:
                self._root_location = PureWindowsPath(root_location).as_posix()

    @staticmethod
    def _parse_location(location: str, root_location: str | None = None) -> str:
        assert location is not None, "Location can't be None"

        if not location.startswith("http"):

            # Check if loc is an absolute path
            path = Path(location)
            if path.is_absolute():
                # If the location is absolute, we assume that this is on purpose
                # and that DATAIO_ROOT should not be used.
                # If it is not absolute, we assume that BONSAI_HOME is the root
                # folder.
                return str(path)
            else:
                if root_location:
                    return str(root_location / path)
                else:
                    bonsai_home = os.getenv("DATAIO_ROOT", None)
                    assert bonsai_home, EnvironmentError(
                        "DATAIO_ROOT environmental varaible is not set, this needs to be set if you are not using an API location."
                    )
                    bonsai_home = Path(bonsai_home)
                    return str(bonsai_home / path)
        else:
            return location

    @staticmethod
    def _replace_variables_in_location_string(
        location: str,
        name=None,
        task_name=None,
        stage=None,
        data_version=None,
        code_version=None,
    ):
        if "{name}" in location or "{resource_name}" in location:
            assert (
                name
            ), "Tried to replace {name} or {resource_name} in location string but name is not set."
            location = location.replace("{name}", name)
            location = location.replace("{resource_name}", name)

        if "{task_name}" in location:
            assert (
                task_name
            ), "Tried to replace {task_name} in location string but task_name is not set."
            location = location.replace("{task_name}", task_name)

        if "{stage}" in location:
            assert (
                stage
            ), "Tried to replace {stage} in location string but stage is not set."
            location = location.replace("{stage}", stage)

        if "{data_version}" in location or "{version}" in location:
            assert (
                data_version
            ), "Tried to replace {data_version} or {version} in location string but data_version is not set."
            location = location.replace("{data_version}", data_version)
            location = location.replace("{version}", data_version)

        if "{code_version}" in location:
            assert (
                code_version
            ), "Tried to replace {code_version} in location string but code_version is not set."
            location = location.replace("{code_version}", code_version)

        return location

    def _parse_name_from_location(self):
        if "http" in str(self.location):
            self._parse_url()
        else:
            self._parse_path()

    def to_pandas(self) -> pd.DataFrame:
        """
        Converts instances of BaseToolModel within BaseTableClass to a pandas DataFrame.

        Returns:
            pandas.DataFrame: DataFrame containing data from instances of BaseToolModel.
        """
        model_dict = self.model_dump()
        model_dict["location"] = self._location
        return pd.DataFrame.from_dict(model_dict, orient="index").T

    def _parse_url(self):
        import urllib

        parsed_source = urllib.parse.urlparse(self.location)
        ls_path_name = parsed_source.path.split("/")
        self.name = ls_path_name[-1] if ls_path_name[-1] else ls_path_name[-2]

    def _parse_path(self):
        self.name = Path(self.location).name

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
