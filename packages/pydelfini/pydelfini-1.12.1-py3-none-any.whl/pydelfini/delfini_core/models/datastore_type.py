from enum import Enum


class DatastoreType(str, Enum):
    LOCAL = "local"
    PLUGIN = "plugin"
    S3 = "s3"

    def __str__(self) -> str:
        return str(self.value)
