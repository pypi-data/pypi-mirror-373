from enum import Enum


class StatusEnum(str, Enum):
    ENDED = "ended"
    OPEN = "open"
    SCHEDULED = "scheduled"

    def __str__(self) -> str:
        return str(self.value)
