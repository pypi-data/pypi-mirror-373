from enum import Enum


class MarketplaceIntegrationStatusesCountStatusItem(str, Enum):
    ACTIVE = "Active"
    DISCONNECTED = "Disconnected"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
