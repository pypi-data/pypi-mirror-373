from enum import Enum


class SearchSearchAccountsBodyTypesItem(str, Enum):
    ACCOUNT = "account"
    PROJECT = "project"

    def __str__(self) -> str:
        return str(self.value)
