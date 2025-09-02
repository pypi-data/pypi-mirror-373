from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd


class TableType(Enum):
    FACT = "fact"
    DIMENSION = "dim"


class TableColumn(Enum):
    CODE = "code"
    DESCRIPTION = "description"


class DataReader:
    def __init__(self, source: Union[Path, str]):
        self.source = source

    def _read_pickle(self, **kwargs):
        pickle_data = pd.read_pickle(self.source, **kwargs)

        return pickle_data

    def _read_csv(self, **kwargs):
        csv_data = pd.read_csv(self.source, **kwargs)

        return csv_data

    def _read_excel(self, **kwargs):
        excel_data = pd.read_excel(self.source, **kwargs)

        return excel_data

    def _read_parquet(self, **kwargs):
        parquet_data = pd.read_parquet(self.source, **kwargs)
        return parquet_data

    def _read_http(self, **kwargs):
        from dataio.utils.connectors import Connector, ConnectorRepository

        connector_repository = ConnectorRepository()
        token = connector_repository.connector_factory.create(self.source).token
        # TODO: only use connector_repository (@Fan 2024-11-19 16:55:35)
        return Connector(self.source, token, **kwargs).get_df()

    def read(self, *args, **kwargs) -> pd.DataFrame:
        str_path = str(self.source)
        if ".pkl" in str_path:
            df = self._read_pickle(*args, **kwargs)
        elif ".csv" in str_path:
            df = self._read_csv(*args, **kwargs)
        elif ".xls" in str_path:
            df = self._read_excel(*args, **kwargs)
        elif ".parquet" in str_path:
            df = self._read_parquet(*args, **kwargs)
        elif "http" in str_path:
            df = self._read_http(*args, **kwargs)

        else:
            raise ValueError(f"Failed to import {str_path}")

        return df


class DataWriter:
    def __init__(self, conn: Union[Path, str]):
        self.conn = conn

    def _validate_conn(self):
        # Check if the connection is a valid file path or URL
        if isinstance(self.conn, Path) or isinstance(self.conn, str):
            if "http" in str(self.conn):
                pass
            else:
                # Assume it's a file path, check for valid file extension
                valid_extensions = [".pkl", ".csv", ".xls", ".xlsx", ".parquet"]
                if not any(ext in str(self.conn) for ext in valid_extensions):
                    raise ValueError(
                        f"Unsupported file extension or connection: {self.conn}"
                    )
        else:
            raise TypeError("Connection must be a Path or string type.")

    def _write_pickle(self, data: pd.DataFrame, **kwargs):
        data.to_pickle(self.conn, **kwargs)

    def _write_csv(self, data: pd.DataFrame, **kwargs):
        data.to_csv(self.conn, **kwargs)

    def _write_excel(self, data: pd.DataFrame, **kwargs):
        data.to_excel(self.conn, **kwargs)

    def _write_parquet(self, data: pd.DataFrame, **kwargs):
        data.to_parquet(self.conn, **kwargs)

    def _write_http(self, data: pd.DataFrame, **kwargs):
        from dataio.utils.connectors import Connector

        return Connector(self.conn).post(data, **kwargs)

    def write(self, data: pd.DataFrame, **kwargs) -> None:
        assert isinstance(data, pd.DataFrame)
        if ".pkl" in str(self.conn):
            self._write_pickle(data, **kwargs)
        elif ".csv" in str(self.conn):
            self._write_csv(data, **kwargs)
        elif ".xls" in str(self.conn):
            self._write_excel(data, **kwargs)
        elif ".parquet" in str(self.conn):
            self._write_parquet(data, **kwargs)

        elif "http" in str(self.conn):
            self._write_http(data, **kwargs)

        else:
            raise ValueError(f"Failed to write resource to destination: {self.conn}")
