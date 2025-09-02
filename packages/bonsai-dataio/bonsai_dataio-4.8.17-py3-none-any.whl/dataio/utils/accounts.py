import json
import os
import random
import string
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Account:
    name: str
    abbreviation: str


class AccountRepository:
    def __init__(
        self,
        path: Path = None,
    ):
        self.file_path = path
        self.accounts = {}
        self.load_accounts()

    def load_accounts(self):
        # breakpoint()
        with open(self.file_path, "r") as file:
            accounts_data = json.load(file)
            self.accounts = {
                name: Account(name, data["abbreviation"])
                for name, data in accounts_data.items()
            }

    def add_account(self, name: str) -> Account:
        if name in self.accounts:
            return self.accounts[name]
        abbreviation = self.generate_abbreviation(name)
        self.accounts[name] = Account(name, abbreviation)
        self.save_accounts()  # Save the updated accounts list to a file or database
        print(f"{name} added to accounts with an abbriviated name of {abbreviation}")
        return self.accounts[name]

    def generate_abbreviation(self, name: str) -> str:
        # Generate a two-letter abbreviation not already used
        while True:
            abbreviation = "".join(random.choices(string.ascii_uppercase, k=2))
            if all(
                abbreviation != acct.abbreviation for acct in self.accounts.values()
            ):
                return abbreviation

    def save_accounts(self):
        with open(self.file_path, "w") as file:
            json_data = {
                name: asdict(account) for name, account in self.accounts.items()
            }
            json.dump(json_data, file, indent=4)

    def get_account(self, name: str) -> Account:
        account = self.accounts.get(name)
        if account is None:
            raise KeyError(f"Account {name} not found")
        return account

    def get_or_create_account(self, name: str) -> Account:
        try:
            return self.get_account(name)
        except KeyError:
            return self.add_account(name)
