from enum import Enum


class MarketplaceOfferingFilesListOItem(str, Enum):
    CREATED = "created"
    NAME = "name"
    VALUE_0 = "-created"
    VALUE_1 = "-name"

    def __str__(self) -> str:
        return str(self.value)
