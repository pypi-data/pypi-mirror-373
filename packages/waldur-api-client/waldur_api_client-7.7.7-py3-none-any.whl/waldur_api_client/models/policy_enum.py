from enum import Enum


class PolicyEnum(str, Enum):
    AFFINITY = "affinity"

    def __str__(self) -> str:
        return str(self.value)
