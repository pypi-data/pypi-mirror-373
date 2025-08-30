from enum import Enum


class ProtocolEnum(str, Enum):
    ICMP = "icmp"
    TCP = "tcp"
    UDP = "udp"

    def __str__(self) -> str:
        return str(self.value)
