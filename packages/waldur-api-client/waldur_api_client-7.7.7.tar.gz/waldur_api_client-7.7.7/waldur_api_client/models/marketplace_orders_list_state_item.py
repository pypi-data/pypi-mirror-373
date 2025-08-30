from enum import Enum


class MarketplaceOrdersListStateItem(str, Enum):
    CANCELED = "canceled"
    DONE = "done"
    ERRED = "erred"
    EXECUTING = "executing"
    PENDING_CONSUMER = "pending-consumer"
    PENDING_PROJECT = "pending-project"
    PENDING_PROVIDER = "pending-provider"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
