from enum import Enum


class MarketplaceOfferingFilesListFieldItem(str, Enum):
    CREATED = "created"
    FILE = "file"
    NAME = "name"
    OFFERING = "offering"
    URL = "url"
    UUID = "uuid"

    def __str__(self) -> str:
        return str(self.value)
