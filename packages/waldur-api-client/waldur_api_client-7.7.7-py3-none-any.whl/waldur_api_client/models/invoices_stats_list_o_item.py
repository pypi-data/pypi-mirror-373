from enum import Enum


class InvoicesStatsListOItem(str, Enum):
    CREATED = "created"
    MONTH = "month"
    VALUE_0 = "-created"
    VALUE_1 = "-month"
    VALUE_2 = "-year"
    YEAR = "year"

    def __str__(self) -> str:
        return str(self.value)
