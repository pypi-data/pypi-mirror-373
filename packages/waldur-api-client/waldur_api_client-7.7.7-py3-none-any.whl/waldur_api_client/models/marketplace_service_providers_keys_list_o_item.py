from enum import Enum


class MarketplaceServiceProvidersKeysListOItem(str, Enum):
    NAME = "name"
    VALUE_0 = "-name"

    def __str__(self) -> str:
        return str(self.value)
