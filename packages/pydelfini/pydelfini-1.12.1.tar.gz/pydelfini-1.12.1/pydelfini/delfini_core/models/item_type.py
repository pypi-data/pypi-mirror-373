from enum import Enum


class ItemType(str, Enum):
    DATAVIEW = "dataview"
    DICTIONARY = "dictionary"
    FILE = "file"
    FOLDER = "folder"
    LINK = "link"

    def __str__(self) -> str:
        return str(self.value)
