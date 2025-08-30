from enum import Enum


class ProposalReviewsListStateItem(str, Enum):
    CREATED = "created"
    IN_REVIEW = "in_review"
    REJECTED = "rejected"
    SUBMITTED = "submitted"

    def __str__(self) -> str:
        return str(self.value)
