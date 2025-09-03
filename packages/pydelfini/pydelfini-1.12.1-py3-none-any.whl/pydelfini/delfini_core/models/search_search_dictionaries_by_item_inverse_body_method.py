from enum import Enum


class SearchSearchDictionariesByItemInverseBodyMethod(str, Enum):
    FULL = "full"

    def __str__(self) -> str:
        return str(self.value)
