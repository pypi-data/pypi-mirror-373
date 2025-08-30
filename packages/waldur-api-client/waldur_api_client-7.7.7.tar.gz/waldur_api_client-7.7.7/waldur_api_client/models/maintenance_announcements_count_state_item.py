from enum import Enum


class MaintenanceAnnouncementsCountStateItem(str, Enum):
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    DRAFT = "Draft"
    IN_PROGRESS = "In progress"
    SCHEDULED = "Scheduled"

    def __str__(self) -> str:
        return str(self.value)
