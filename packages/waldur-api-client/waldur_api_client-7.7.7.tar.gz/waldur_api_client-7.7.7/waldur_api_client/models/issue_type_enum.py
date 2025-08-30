from enum import Enum


class IssueTypeEnum(str, Enum):
    CHANGE_REQUEST = "Change Request"
    INCIDENT = "Incident"
    INFORMATIONAL = "Informational"
    SERVICE_REQUEST = "Service Request"

    def __str__(self) -> str:
        return str(self.value)
