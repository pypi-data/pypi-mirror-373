from enum import Enum


class OpenstackPortsListOItem(str, Enum):
    NETWORK_NAME = "network_name"
    VALUE_0 = "-network_name"

    def __str__(self) -> str:
        return str(self.value)
