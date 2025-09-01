from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import List, Union

from dataio.utils.accounts import AccountRepository
from dataio.utils.schema_enums import APIEndpoints


@dataclass
class Version:
    name: str
    acronym: str
    version_date: str  # Default Date in YYYY-MM-DD format
    version_semantic: str = None
    is_latest: bool = True

    def has_valid_version_date_format(self, expected_format: str = "%Y-%m-%d") -> bool:
        """
        Checks if the version_date is in the expected format.
        """
        try:
            datetime.strptime(self.version_date, expected_format)
            return True
        except ValueError:
            logging.warning(
                f"The current version date is in {self.version_date}. Please consider using recommended format: {expected_format}"
            )
            return False

    def parse_date(self, from_format: str = "%Y-%m-%d", to_format: str = "%Y%m%d"):
        """
        Parses the version_date from 'YYYY-MM-DD' to 'YYYYMMDD' format.
        """
        print(f"parsing date from {from_format} to {to_format}")
        parsed_date = datetime.strptime(self.version_date, from_format).strftime(
            to_format
        )
        self.version_date = parsed_date
        return self

    def update_version_date(self, version_date: str):
        """
        Updates the version_date to a new date provided in 'YYYY-MM-DD' format.
        """
        # Check if the new date is in the correct format
        try:
            date = datetime.strptime(version_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            self.version_date = date
        except ValueError:
            print(f"Unexpected date format: {version_date}. Expected format: %Y-%m-%d")
        return self

    def to_json(self):
        data = asdict(self)

        return json.dumps(data)


class VersionCollection:
    def __init__(
        self,
        versions: List[Version],
        source: str | Path = None,
        account_repo: AccountRepository = None,
    ):
        self.versions = versions
        self.source = source
        default_account = (
            Path(os.environ.get("BONSAI_HOME")) / "_bonsai" / "accounts.json"
        )
        self.account_repo = account_repo or AccountRepository(default_account)

    @classmethod
    def load_from(cls, source: Union[Path, str]):
        if isinstance(source, str):
            versions = APIVersionSource(url=source).load()
        elif isinstance(source, Path):
            versions = TXTVersionSource(path=source).load()
        else:
            raise TypeError(f"version from {source} is not supported.")

        if not versions:
            raise ValueError(f"No versions found from neither {str(source)} nor API")
        return versions

    def get_account_versions(self, account: str) -> List[Version]:
        account_versions = [v for v in self.versions if v.name == account]
        if not account_versions:
            raise ValueError(f"No version found for account {account}")

        return account_versions

    def update_account_version_date(self, account_name: str, version_date: str):
        """Replace the version_date of account in version collection with a new version_date"""
        account = self.account_repo.get_or_create_account(account_name)
        try:
            account_version = self.get_latest_version(account.name)
            self.versions.remove(account_version)
            account_version.update_version_date(version_date)
            self.versions.append(account_version)
            self.save()
        except ValueError:
            print(f"Adding a new version record for {account.name}.")
            self.add_account_version(
                account_name=account_name, version_date=version_date
            )

    def get_latest_version(self, account: str) -> Version:
        account_versions = self.get_account_versions(account)

        latest_version = max(account_versions, key=lambda x: x.version_date)
        if not latest_version:
            raise ValueError(
                f"No version is assigned with the latest version for account {account}"
            )
        return latest_version

    def add_account_version(
        self,
        account_name: str,
        version_date: str,
        is_latest: bool = True,
        version_semantic: str = None,
    ) -> Version:
        """
        Adds a new version for an account. If the account does not exist, it adds the account.
        """
        # Ensure the account exists in the AccountRepository
        account = self.account_repo.get_or_create_account(account_name)

        # Check if a version with the same date already exists to prevent duplicates
        try:
            self.get_account_versions(account.name)
        except ValueError:
            print(
                f"No version found for account {account.name}, will add a new version using {version_date} for the account"
            )
        # Create a new version instance
        new_version = Version(
            name=account.name,
            acronym=account.abbreviation,
            version_date=version_date,
            version_semantic=version_semantic,
            is_latest=is_latest,
        )

        self.versions.append(new_version)
        # Optionally save the updated versions list
        self.save()

        return new_version

    def to_api(self, url: str = "https://lca.aau.dk/api/datasets/"):
        APIVersionSource(url).save()

    def to_txt(self, path: Path):
        TXTVersionSource(path=path).save(self.versions)

    def save(self):
        if isinstance(self.source, Path):
            self.to_txt(self.source)
        elif isinstance(self.source, str):
            self.to_api(self.source)
        else:
            raise ValueError("Unknown version source type.")


class VersionSource(ABC):
    @abstractmethod
    def load(self) -> VersionCollection:
        raise NotImplementedError

    @abstractmethod
    def save(self, versions: list[Version]):
        raise NotImplementedError


class APIVersionSource:
    def __init__(self, name: str = APIEndpoints.METADATA.name) -> None:
        self.name = name
        from dataio.utils.connectors import connector_repository

        self.api_connector = connector_repository.get(name=self.name)

    def load(self) -> VersionCollection:
        api_response = self.api_connector.get()
        version_fields = {field.name for field in fields(Version)}
        versions = []
        for metadata in api_response:
            version_data = {k: v for k, v in metadata.items() if k in version_fields}
            version_instance = Version(**version_data)
            version_instance.parse_date()
            versions.append(version_instance)
        if not versions:
            raise ValueError(f"No version found from {self.url}")
        return VersionCollection(versions, source=self.url)

    def save(self, versions: list[Version]):

        ls_version = []
        for version in versions:
            if not version.has_valid_version_date_format():
                version.parse_date(from_format="%Y%m%d", to_format="%Y-%m-%d").to_json()
            ls_version.append(version.to_json())

        return self.api_connector.post(ls_version)


class TXTVersionSource:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self):
        """
        read the version-date of a previously produced dataset
            Here the list of datasets (in key) and the acronym
            inserted in the version.txt:

        parameters
        --------------
        path: path of the version file.

        """
        "dictionary to link datasets to acronyms used in version file"
        default_account = (
            Path(os.environ.get("BONSAI_HOME")) / "_bonsai" / "accounts.json"
        )
        account_repo = AccountRepository(default_account)

        with open(self.path, "r") as file:
            version_txt = file.read()

        versions = []
        for account in account_repo.accounts.values():
            # position where the date to read starts
            start_change = version_txt.find(account.abbreviation) + 4
            if start_change < 4:
                logging.info(
                    f"Acronym {account.abbreviation} for account {account.name} not found in the source: {str(self.path)}."
                )
                continue

            # date to read
            date_to_read = version_txt[start_change : start_change + 10]

            account_version = Version(
                name=account.name,
                acronym=account.abbreviation,
                version_date=date_to_read,
            )
            if not account_version.has_valid_version_date_format():
                account_version.parse_date(from_format="%Y%m%d", to_format="%Y-%m-%d")
                logging.info(f"parsing date for {account} successful")
            versions.append(account_version)
        return VersionCollection(versions, source=self.path)

    def save(self, versions: list[Version]):
        with open(self.path, "w") as file:
            for version in versions:
                if not version.has_valid_version_date_format():
                    version.parse_date(from_format="%Y%m%d", to_format="%Y-%m-%d")
                file.write(f"{version.acronym}='{version.version_date}'" + "\n")
