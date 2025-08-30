from enum import Enum


class ProposalReviewsCountOItem(str, Enum):
    CREATED = "created"
    STATE = "state"
    VALUE_0 = "-created"
    VALUE_1 = "-state"

    def __str__(self) -> str:
        return str(self.value)
