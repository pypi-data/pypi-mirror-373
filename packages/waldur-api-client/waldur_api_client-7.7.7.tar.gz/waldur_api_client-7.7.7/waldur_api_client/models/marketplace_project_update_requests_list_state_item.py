from enum import Enum


class MarketplaceProjectUpdateRequestsListStateItem(str, Enum):
    APPROVED = "approved"
    CANCELED = "canceled"
    DRAFT = "draft"
    PENDING = "pending"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
