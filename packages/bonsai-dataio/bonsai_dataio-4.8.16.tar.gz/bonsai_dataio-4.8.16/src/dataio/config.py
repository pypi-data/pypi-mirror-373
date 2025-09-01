# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 16:05:31 2022

@author: ReMarkt
"""
import copy
from dataclasses import fields
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
import yaml

from dataio.resources import ResourceRepository
from dataio.utils.path_manager import PathBuilder

logger = logging.getLogger("config")


class Config:

    @staticmethod
    def get_airflow_defaults(filename: str):
        """
        Load config from airflow or from src/config/airflow_attributes.config.json
        Args:
            filename (str): JSON config file located in the folder 'src/config'
        Returns: None
        """
        config_path = Path(__file__).parent.parent / "config" / filename

        logger.debug("path= " + str(config_path))
        try:
            with open(config_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(
                f"Config file '{filename}' not found, please create it in the folder src/config"
            )

    def __init__(
        self,
        current_task_name=None,
        custom_resource_path=None,
        log_level=logging.WARNING,
        log_file=None,
        run_by_user=None,
        **kwargs,
    ):
        """
        Config class for managing configurations, including logging.

        :param current_task_name: Name of the current task (used for logging).
        :param custom_resource_path: Optional path for custom resources.
        :param log_level: Logging level (default: WARNING).
        :param log_file: Optional file path to log output.
        :param kwargs: Additional configuration parameters.
        """

        self.current_task_name = current_task_name
        self.custom_resource_path = custom_resource_path
        self.run_by_user = run_by_user

        self._load_config("data_attributes.config.yaml")
        self._load_airflow_config("airflow_attributes.config.json")

        # Set up logging
        self.log_handler = logging.StreamHandler()
        self.log_level = log_level
        self.logger = self._setup_logger(log_file)

        # Assign additional configuration attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
            if key == "config_path":
                self._load_config(value, True)

    def _setup_logger(self, log_file):
        """
        Sets up the logger with a console handler and optional file handler.
        """
        logger = logging.getLogger(self.current_task_name)
        logger.setLevel(self.log_level)

        # Prevent duplicate log handlers
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)

            # Formatter
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # File handler (if provided)
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(self.log_level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

        return logger

    def log(self, level, message):
        """
        Logs a message with the specified logging level.
        """
        if self.logger:
            self.logger.log(level, message)

    def load_env(self) -> dict:
        load_dotenv()
        env_dict = {}

        for key in os.environ:
            env_dict[key] = os.environ[key]
        return env_dict

    @property
    def bonsai_home(self):
        """environment variable to define the home directory for dataio"""
        env_dict = self.load_env()
        assert env_dict[
            "BONSAI_HOME"
        ], "Please set up environmental variable for 'BONSAI_HOME'"
        return Path(env_dict.get("BONSAI_HOME", str(Path.home())))

    @property
    def dataio_root(self):
        """environment variable to define the home directory for hybrid_sut"""
        env_dict = self.load_env()
        assert env_dict[
            "DATAIO_ROOT"
        ], "Please set up environmental variable for 'DATAIO_ROOT'"
        return Path(env_dict.get("DATAIO_ROOT", str(Path.home())))

    @property
    def path_repository(self) -> PathBuilder:

        from dataio.utils.accounts import AccountRepository
        from dataio.utils.versions import VersionCollection

        print(f"Get version from {self.version_source}")
        return PathBuilder(
            Path(self.bonsai_home),
            version_repo=VersionCollection.load_from(self.version_source),
            account_repository=AccountRepository(
                self.bonsai_home / "_bonsai" / "accounts.json"
            ),
        )

    @property
    def version_source(self):
        vdate = self.date.replace("-", "")

        path_version = self.bonsai_home / "versions" / f"versions_{vdate}.txt"
        if not path_version.exists():
            path_version = (
                self.bonsai_home / "_bonsai" / "versions" / f"versions_{vdate}.txt"
            )
            if not path_version.exists():
                import shutil

                shutil.copy(
                    self.bonsai_home
                    / "_bonsai"
                    / "versions"
                    / f"versions_{self.LATEST_VERSION_DATE.replace('-','')}.txt",
                    path_version,
                )

        # TODO: replace this path with Version class
        return path_version

    @version_source.setter
    def version_source(self, path: Path) -> None:
        self.version_source = path

    @property
    def schemas(self):
        from dataio.schemas import bonsai_api

        return bonsai_api

    @property
    def schema_enums(self):
        from dataio.utils import schema_enums

        return schema_enums

    @property
    def connector_repository(self):
        from dataio.utils.connectors import connector_repository

        return connector_repository

    def list_parameters(self):
        """List all dataclass field names."""

        return [field.name for field in fields(self)]

    @property
    def resource_repository(self) -> ResourceRepository:
        from dataio.resources import ResourceRepository

        db_path = (
            self.custom_resource_path if self.custom_resource_path else self.dataio_root
        )

        return ResourceRepository(db_path=db_path)

    @property
    def sut_resource_repository(self):
        from dataio.utils.hsut.resources_hsut import (
            CSVResourceRepository as SutCSVResourceRepository,
        )

        db_path = (
            self.path_repository.exiobase4
            if self.path_repository.exiobase4
            else self.bonsai_home
        )

        return SutCSVResourceRepository(db_path)

    @property
    def classif_repository(self):
        return {
            "link_to_NACE_classif.csv": self.path_repository.exiobase4
            / "Classification"
            / "link_to_NACE_classif.csv",
            "Master_classif_exio4.xlsx": self.path_repository.classification
            / "Master_classif_exio4.xlsx",
            "fao_product_child_parent_classif.csv": self.path_repository.classification
            / "fao"
            / "fao_product_child_parent_classif.csv",  # NOTE: external classif, this is a classif for FAO (@Fan 2024-11-11 13:03:00)
            "fao_item_class.csv": self.path_repository.classification
            / "fao_item_class.csv",  # NOTE: external classif, this is a classif for FAO (@Fan 2024-11-11 13:03:00)
            "old_fao_item_class.csv": self.path_repository.classification
            / "old"
            / "fao_item_class.csv",  # NOTE: external classif, this is a classif for FAO (@Fan 2024-11-11 13:03:00)
            "activity_classif.pkl": self.path_repository.classification
            / "activity_classif.pkl",  # NOTE: external classif, this is a classification table that bridges EXIO monetary classification description to its code. (Fan 2024-11-11 13:02:02)
            "product_classification_monetary.csv": self.path_repository.classification
            / "product_classification_monetary.csv",  # NOTE: external classif, this is a product classif for exiobase3.3 hybrid table (@Fan 2024-09-24 11:39:39)
            "activities": self.connector_repository.get("ACTIVITIES").url,
            "products": self.connector_repository.get("PRODUCTS").url,
            "locations": self.connector_repository.get("LOCATIONS").url,
        }

    @property
    def corr_repository(self):
        return {
            "exiov4_prod_vs_markets.xlsx": self.path_repository.correspondence
            / "exio4_other"
            / "exiov4_prod_vs_markets.xlsx",  # TODO: this is an activity-to-product correspondence, needs additional correspdence (@Fan 2024-11-10 21:43:11)
            "IEAvsExiobase_products.xlsx": self.path_repository.correspondence
            / "IEA"
            / "IEAvsExiobase_products.xlsx",  # TODO: "fuel_to_elec" is a product-to-activity correspondence
            # TODO: "act_vs_iea" is a parent-child relationship table. (@Fan 2024-11-10 21:49:39)
            "Emission_genric_correspondence.xlsx": self.path_repository.correspondence
            / "emissions"
            / "Emission_genric_correspondence.xlsx",  # TODO: needs an additional emission classification that has not been decided yet (@Fan 2024-11-10 22:26:17)
            "waste_corresp_exiob_3vs4.xlsx": self.path_repository.correspondence
            / "waste"
            / "waste_corresp_exiob_3vs4.xlsx",  # TODO: this corresponde requires a difference schema than the usual ones (@Fan 2024-11-08 10:26:38)
            "Fertilisers_hs_FAO_vs_exiobase.xlsx": self.path_repository.correspondence
            / "fao"
            / "Fertilisers_hs_FAO_vs_exiobase.xlsx",  # TODO: requires additional changes in schema to fully remove this correspondence (@Fan 2024-11-10 21:40:33)
            "D1_D0_e0_f0_dm_kpr_2+.xls": self.path_repository.correspondence
            / "exio_v3_vs_v4"
            / "D1_D0_e0_f0_dm_kpr_2+.xls",  # TODO: this is an activity-to-prouduct correspondence, needs additional correspondence table (@Fan 2024-11-10 21:42:29)
            "Exio_vs_concito_simapro_emissions.xls": self.path_repository.correspondence
            / "concito"
            / "Exio_vs_concito_simapro_emissions.xls",  # TODO: needs an elementary flow classification table. (@Fan 2024-11-11 13:09:53)
            f"Corr_FAO_exio_{self.fao_cfile}.xlsx": self.path_repository.correspondence
            / "fao"
            / f"Corr_FAO_exio_{self.fao_cfile}.xlsx",  # TODO: there is a product-to-activity correspondence (@Fan 2024-11-10 22:20:21)
            "Exio_4_classif_bridge_for_LCI_coeff.xlsx": self.path_repository.correspondence
            / "exio_v3_vs_v4"
            / "Exio_4_classif_bridge_for_LCI_coeff.xlsx",  # TODO: there are some weird names that does not exist in the classification yet, and maybe should be modified (@Fan )
            "location-corr": self.connector_repository.get("LOCATION_CORR").url,
            "activity-corr": self.connector_repository.get("ACTIVITY_CORR").url,
            "product-corr": self.connector_repository.get("PRODUCT_CORR").url,
        }

    def _load_config(self, filename: str, isLocalfile: bool = False) -> None:
        """Load config file in the class Config's attributes
        Args:
            filename (str): YAML config file located in the folder 'src/config'
        Returns: None
        """
        config_path = (
            Path(filename)
            if isLocalfile
            else Path(__file__).parent.parent / "config" / filename
        )

        logger.debug(f"path= {config_path}")
        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                for key, value in config.items():
                    self.__setattr__(key, value)
            return None
        except FileNotFoundError:
            raise Exception(
                f"Config file '{filename}' not found, please create it, or one in the folder src/config"
            )

    def _load_airflow_config(self, filename: str):
        """
        Load config from airflow or from src/config/airflow_attributes.config.json
        Args:
            filename (str): JSON config file located in the folder 'src/config'
        Returns: None
        """

        airflow_defaults = Config.get_airflow_defaults(filename)
        for key, value in airflow_defaults.items():
            self.__setattr__(key, value)

    def copy(self):
        """
        Creates a deep copy of the current Config instance.
        """
        return copy.deepcopy(self)
