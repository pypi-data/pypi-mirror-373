import json
import logging
import os
from getpass import getpass
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import requests
from dotenv import load_dotenv

from dataio.utils.schema_enums import APIEndpoints

load_dotenv()


# TODO: seperate cache logic out (@Fan 2024-10-24 13:52:30)
class Connector:
    def __init__(self, url, token: str = None):
        self.url = url
        # Check if the token was passed explicitly, otherwise try loading it from cache
        self.token = token

    def parse_url(self): ...

    def _set_header(self):

        if self.token:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Token {self.token}",
            }
        else:
            headers = {
                "Accept": "application/json",
            }
        return headers

    def get(self):
        try:
            response = requests.get(self.url, headers=self._set_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception(
                    f"Unauthorized: Your token {self.token} is not correctly setup."
                ) from e
            elif response.status_code == 429:
                raise Exception(
                    "Too many requests: Please wait and try again later."
                ) from e
        data = response.json()

        if "results" in data:
            return self._parse_paginated_response(data)
        else:
            return self._parse_non_paginated_response(data)

    def _parse_paginated_response(self, data):
        results = data["results"]
        while data.get("next"):
            response = requests.get(data["next"], headers=self._set_header())
            data = response.json()
            results.extend(data["results"])
        return results

    def _parse_non_paginated_response(self, data):
        return data

    def get_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.get())

    def _pre_payload(
        self, data: Union[pd.DataFrame, pd.Series], chunk_size=None
    ) -> str:

        if isinstance(data, pd.DataFrame):
            if chunk_size is not None:
                # Creating chunks using list comprehension
                return [
                    data.iloc[i : i + chunk_size].to_json(orient="records")
                    for i in range(0, data.shape[0], chunk_size)
                ]
            else:
                return [data.to_json(orient="records")]
        # Check if the input data is a pandas Series
        elif isinstance(data, pd.Series):
            return [data.to_json(orient="index")]
        else:
            raise ValueError("Input data must be a pandas DataFrame or Series")

    def post(self, data: Union[pd.DataFrame, pd.Series], **kwargs):

        chunk_size = kwargs.pop("chunk_size", None)
        payloads = self._pre_payload(data, chunk_size=chunk_size)
        results = []
        for payload in payloads:
            payload_json = json.loads(payload)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {self.token}",
            }
            response = requests.post(
                self.url, json=payload_json, headers=headers, **kwargs
            )  # Use remaining kwargs here
            if response.status_code == 201:
                results.append(response.json())
            else:
                raise Exception(
                    f"Post failed with status code {response.status_code}: {response.text}"
                )
        return results

    def put(self, data: Union[pd.DataFrame, pd.Series], **kwargs):
        chunk_size = kwargs.pop("chunk_size", None)
        payloads = self._pre_payload(data, chunk_size=chunk_size)
        results = []
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}",
        }

        for payload in payloads:
            payload_json = json.loads(payload)

            # If the payload is a list of records (from DataFrame)
            if isinstance(payload_json, list):
                for item in payload_json:
                    code = item.get("code")
                    if not code:
                        raise ValueError("Each item must contain a 'code' key.")
                    url_with_code = f"{self.url}/{code}"
                    response = requests.put(
                        url_with_code, json=item, headers=headers, **kwargs
                    )
                    if response.ok:
                        try:
                            results.append(response.json())
                        except ValueError:
                            results.append(None)
                    else:
                        raise Exception(
                            f"PUT failed with status code {response.status_code}: {response.text}"
                        )
            # If the payload is a single record (from Series)
            elif isinstance(payload_json, dict):
                code = payload_json.get("code")
                if not code:
                    raise ValueError("Data must contain a 'code' key.")
                url_with_code = f"{self.url}/{code}"
                response = requests.put(
                    url_with_code, json=payload_json, headers=headers, **kwargs
                )
                if response.ok:
                    try:
                        results.append(response.json())
                    except ValueError:
                        results.append(None)
                else:
                    raise Exception(
                        f"PUT failed with status code {response.status_code}: {response.text}"
                    )
            else:
                raise ValueError("Payload must be a dict or list of dicts.")

        return results


class ConnectorFactory:
    def __init__(self):
        self.cached_token = None

    def create(self, url: str):
        # TODO: token use configuration should be in Config class insted of ConnectorFactory (@Fan 2024-11-15 16:09:40)
        token = self._get_token()
        return Connector(url, token)

    def _get_token(self) -> str:
        """
        Retrieves a token from cache, environment, or prompts for credentials if none found.
        """
        if not self.cached_token:
            self.cached_token = self._load_token_from_cache() or os.environ.get(
                "BONSAI_TOKEN"
            )
            if not self.cached_token:

                # TODO: there should be a way to update token use setting (@Fan 2024-11-15 16:09:46)
                config = self._load_config()
                if not config["use_token"]:
                    return None
                else:
                    self.cached_token = self._prompt_for_credentials()
        return self.cached_token

    def _prompt_for_credentials(self) -> str:
        """
        Prompts the user for credentials and retrieves a token.
        """
        choice = (
            input(
                """
                No token found. Rate limiting is applied to API accessibility.\n
                Do you want to enter credentials to get a token to avoid rate limiting? (y/n): 
                """
            )
            .strip()
            .lower()
        )
        if choice == "y":
            email = input("Enter your email: ")
            password = getpass("Enter your password: ")
            token = self._get_token_from_api(email, password)
            if token:
                self._cache_token(token)
                self._save_user_decision(True)
                return token
            else:
                raise ValueError(
                    "Failed to retrieve token. Please check your credentials."
                )
        elif choice == "n":
            logging.warning(
                "Proceeding without a token. You may encounter rate limits."
            )
            self._save_user_decision(False)
            return ""
        else:
            logging.warning("Invalid choice. Please try again.")
            return self._prompt_for_credentials()

    def _get_token_from_api(self, email: str, password: str) -> str:
        """
        Retrieves a token by making a POST request to the token endpoint.
        """
        token_url = f"{APIEndpoints.BASE_URL.value}{APIEndpoints.TOKEN.value}"
        try:
            response = requests.post(
                token_url, data={"email": email, "password": password}
            )
            response.raise_for_status()
            token = response.json().get("token")
            if token:
                logging.info("Token successfully retrieved.")
                return token
        except requests.RequestException as e:
            logging.error(f"Error retrieving token: {e}")
        return ""

    def _load_token_from_cache(self) -> Optional[str]:
        """
        Loads the token from cache if it exists.
        """
        try:
            token_cache_path = self._get_cache_path()
            if os.path.exists(token_cache_path):
                with open(token_cache_path, "r") as f:
                    data = json.load(f)
                    token = data.get("token")
                    if token:
                        logging.info("Token loaded from cache.")
                        return token
        except IOError as e:
            logging.error(f"Failed to load token from cache: {e}")
        return None

    def _cache_token(self, token: str):
        """
        Saves the token to a cache file.
        """
        try:
            token_cache_path = self._get_cache_path()
            with open(token_cache_path, "w") as f:
                json.dump({"token": token}, f)
            logging.info(f"Token cached successfully at {token_cache_path}.")
        except IOError as e:
            logging.error(f"Failed to cache token: {e}")

    def _get_cache_path(self):
        """
        Returns the path for caching the token.
        """
        from pathlib import Path

        cache_path = Path.home() / ".cache" / "bonsai"
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path / "token_cache.txt"

    def _load_config(self) -> dict:
        """
        Loads the user's choice from a configuration file.
        """
        config_path = self._get_config_path()
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                logging.warning(
                    "Failed to load user decision. Defaulting to use token."
                )
        return {"use_token": True}  # Default to using tokens

    def _save_user_decision(self, use_token: bool):
        """
        Saves the user's choice to a configuration file.
        """
        config_path = self._get_config_path()
        try:
            with open(config_path, "w") as f:
                json.dump({"use_token": use_token}, f)
        except IOError as e:
            logging.error(f"Failed to save user decision: {e}")

    def _get_config_path(self) -> Path:
        """
        Returns the path for the configuration file.
        """
        config_dir = Path.home() / ".cache" / "bonsai"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"


class ConnectorRepository:
    def __init__(self, connector_factory: Optional[ConnectorFactory] = None):
        self.connector_factory = (
            connector_factory if connector_factory else ConnectorFactory()
        )
        self._cache = {}
        self._preload_connectors()

    def get(self, name: str) -> Connector:
        if name not in self._cache:
            url = APIEndpoints.get_url(name)
            self._cache[name] = self.connector_factory.create(url)
        return self._cache[name]

    def _preload_connectors(self):
        """
        Preload all connectors from APIEndpoints except BASE_URL.
        """
        for name in APIEndpoints.__members__:
            if name != "BASE_URL":  # Skip BASE_URL
                try:
                    self.get(name)  # This will cache the connector
                except ValueError as e:
                    logging.warning(f"Failed to preload connector for {name}: {e}")


connector_repository = ConnectorRepository()
