from enum import Enum


class MarketplaceOfferingUsersListOItem(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    USERNAME = "username"
    VALUE_0 = "-created"
    VALUE_1 = "-modified"
    VALUE_2 = "-username"

    def __str__(self) -> str:
        return str(self.value)
