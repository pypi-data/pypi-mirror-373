from enum import Enum


class SystemConfigurationAuthenticationCredentialsType(str, Enum):
    CREDENTIALS = "credentials"

    def __str__(self) -> str:
        return str(self.value)
