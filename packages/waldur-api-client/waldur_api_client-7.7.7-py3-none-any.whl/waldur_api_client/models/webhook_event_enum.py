from enum import Enum


class WebhookEventEnum(str, Enum):
    COMMENT_CREATED = "comment_created"
    COMMENT_DELETED = "comment_deleted"
    COMMENT_UPDATED = "comment_updated"
    JIRAISSUE_DELETED = "jira:issue_deleted"
    JIRAISSUE_UPDATED = "jira:issue_updated"

    def __str__(self) -> str:
        return str(self.value)
