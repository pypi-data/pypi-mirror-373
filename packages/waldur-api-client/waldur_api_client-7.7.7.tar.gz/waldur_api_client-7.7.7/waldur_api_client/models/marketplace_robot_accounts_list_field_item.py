from enum import Enum


class MarketplaceRobotAccountsListFieldItem(str, Enum):
    BACKEND_ID = "backend_id"
    CREATED = "created"
    CUSTOMER_NAME = "customer_name"
    CUSTOMER_UUID = "customer_uuid"
    DESCRIPTION = "description"
    ERROR_MESSAGE = "error_message"
    ERROR_TRACEBACK = "error_traceback"
    FINGERPRINTS = "fingerprints"
    KEYS = "keys"
    MODIFIED = "modified"
    OFFERING_CUSTOMER_UUID = "offering_customer_uuid"
    OFFERING_PLUGIN_OPTIONS = "offering_plugin_options"
    PROJECT_NAME = "project_name"
    PROJECT_UUID = "project_uuid"
    RESOURCE = "resource"
    RESOURCE_NAME = "resource_name"
    RESOURCE_UUID = "resource_uuid"
    RESPONSIBLE_USER = "responsible_user"
    STATE = "state"
    TYPE = "type"
    URL = "url"
    USERNAME = "username"
    USERS = "users"
    USER_KEYS = "user_keys"
    UUID = "uuid"

    def __str__(self) -> str:
        return str(self.value)
