from enum import Enum


class ProposalRequestedOfferingsCountStateItem(str, Enum):
    ACCEPTED = "accepted"
    CANCELED = "canceled"
    REQUESTED = "requested"

    def __str__(self) -> str:
        return str(self.value)
