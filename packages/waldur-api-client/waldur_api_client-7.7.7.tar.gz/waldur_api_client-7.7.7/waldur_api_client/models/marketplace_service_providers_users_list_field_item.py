from enum import Enum


class MarketplaceServiceProvidersUsersListFieldItem(str, Enum):
    AFFILIATIONS = "affiliations"
    EMAIL = "email"
    FIRST_NAME = "first_name"
    FULL_NAME = "full_name"
    IS_ACTIVE = "is_active"
    LAST_NAME = "last_name"
    ORGANIZATION = "organization"
    PHONE_NUMBER = "phone_number"
    PROJECTS_COUNT = "projects_count"
    REGISTRATION_METHOD = "registration_method"
    USERNAME = "username"
    UUID = "uuid"

    def __str__(self) -> str:
        return str(self.value)
