from enum import Enum


class MarketplaceOfferingUsersListFieldItem(str, Enum):
    CREATED = "created"
    CUSTOMER_NAME = "customer_name"
    CUSTOMER_UUID = "customer_uuid"
    IS_RESTRICTED = "is_restricted"
    MODIFIED = "modified"
    OFFERING = "offering"
    OFFERING_NAME = "offering_name"
    OFFERING_UUID = "offering_uuid"
    SERVICE_PROVIDER_COMMENT = "service_provider_comment"
    SERVICE_PROVIDER_COMMENT_URL = "service_provider_comment_url"
    STATE = "state"
    URL = "url"
    USER = "user"
    USERNAME = "username"
    USER_EMAIL = "user_email"
    USER_FULL_NAME = "user_full_name"
    USER_USERNAME = "user_username"
    USER_UUID = "user_uuid"
    UUID = "uuid"

    def __str__(self) -> str:
        return str(self.value)
