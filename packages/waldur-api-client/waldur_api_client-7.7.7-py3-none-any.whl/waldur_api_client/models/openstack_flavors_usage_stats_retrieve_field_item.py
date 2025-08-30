from enum import Enum


class OpenstackFlavorsUsageStatsRetrieveFieldItem(str, Enum):
    BACKEND_ID = "backend_id"
    CORES = "cores"
    DISK = "disk"
    DISPLAY_NAME = "display_name"
    NAME = "name"
    RAM = "ram"
    SETTINGS = "settings"
    URL = "url"
    UUID = "uuid"

    def __str__(self) -> str:
        return str(self.value)
