from enum import Enum


class SystemConfigurationDatastoresLocalType(str, Enum):
    LOCAL = "local"

    def __str__(self) -> str:
        return str(self.value)
