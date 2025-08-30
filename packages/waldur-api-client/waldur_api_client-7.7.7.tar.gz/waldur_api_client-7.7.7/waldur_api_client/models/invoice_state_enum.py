from enum import Enum


class InvoiceStateEnum(str, Enum):
    CANCELED = "canceled"
    CREATED = "created"
    PAID = "paid"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
