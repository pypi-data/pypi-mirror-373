from enum import Enum


class ProjectsRetrieveFieldItem(str, Enum):
    BACKEND_ID = "backend_id"
    BILLING_PRICE_ESTIMATE = "billing_price_estimate"
    CREATED = "created"
    CUSTOMER = "customer"
    CUSTOMER_ABBREVIATION = "customer_abbreviation"
    CUSTOMER_NAME = "customer_name"
    CUSTOMER_NATIVE_NAME = "customer_native_name"
    CUSTOMER_SLUG = "customer_slug"
    CUSTOMER_UUID = "customer_uuid"
    DESCRIPTION = "description"
    END_DATE = "end_date"
    END_DATE_REQUESTED_BY = "end_date_requested_by"
    IMAGE = "image"
    IS_INDUSTRY = "is_industry"
    MARKETPLACE_RESOURCE_COUNT = "marketplace_resource_count"
    MAX_SERVICE_ACCOUNTS = "max_service_accounts"
    NAME = "name"
    OECD_FOS_2007_CODE = "oecd_fos_2007_code"
    OECD_FOS_2007_LABEL = "oecd_fos_2007_label"
    PROJECT_CREDIT = "project_credit"
    RESOURCES_COUNT = "resources_count"
    SLUG = "slug"
    START_DATE = "start_date"
    TYPE = "type"
    TYPE_NAME = "type_name"
    TYPE_UUID = "type_uuid"
    URL = "url"
    UUID = "uuid"

    def __str__(self) -> str:
        return str(self.value)
