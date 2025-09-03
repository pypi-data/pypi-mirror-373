from enum import Enum


class Operations(str, Enum):
    ACCOUNT = "account"
    ADMIN_CDE = "admin.cde"
    ADMIN_CONFIG = "admin.config"
    ADMIN_GRANTADMIN = "admin.grantadmin"
    ADMIN_METADATA = "admin.metadata"
    ADMIN_METRICS = "admin.metrics"
    ADMIN_TASKS = "admin.tasks"
    ADMIN_USERS = "admin.users"
    GROUP = "group"

    def __str__(self) -> str:
        return str(self.value)
