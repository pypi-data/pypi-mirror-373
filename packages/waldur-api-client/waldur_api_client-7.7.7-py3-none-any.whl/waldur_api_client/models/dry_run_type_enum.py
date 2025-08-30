from enum import Enum


class DryRunTypeEnum(str, Enum):
    CREATE = "Create"
    PULL = "Pull"
    TERMINATE = "Terminate"
    UPDATE = "Update"

    def __str__(self) -> str:
        return str(self.value)
