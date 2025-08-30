from enum import Enum


class MarketplaceResourcesListOItem(str, Enum):
    CREATED = "created"
    NAME = "name"
    PROJECT_NAME = "project_name"
    STATE = "state"
    VALUE_0 = "-created"
    VALUE_1 = "-name"
    VALUE_2 = "-project_name"
    VALUE_3 = "-state"

    def __str__(self) -> str:
        return str(self.value)
