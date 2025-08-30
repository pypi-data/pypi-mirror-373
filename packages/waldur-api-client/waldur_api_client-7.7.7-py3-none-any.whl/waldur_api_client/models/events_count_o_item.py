from enum import Enum


class EventsCountOItem(str, Enum):
    CREATED = "created"
    VALUE_0 = "-created"

    def __str__(self) -> str:
        return str(self.value)
