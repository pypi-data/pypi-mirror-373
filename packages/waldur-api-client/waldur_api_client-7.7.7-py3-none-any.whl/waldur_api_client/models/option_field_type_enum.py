from enum import Enum


class OptionFieldTypeEnum(str, Enum):
    BOOLEAN = "boolean"
    DATE = "date"
    HTML_TEXT = "html_text"
    INTEGER = "integer"
    MONEY = "money"
    SELECT_MULTIPLE_OPENSTACK_INSTANCES = "select_multiple_openstack_instances"
    SELECT_MULTIPLE_OPENSTACK_TENANTS = "select_multiple_openstack_tenants"
    SELECT_OPENSTACK_INSTANCE = "select_openstack_instance"
    SELECT_OPENSTACK_TENANT = "select_openstack_tenant"
    SELECT_STRING = "select_string"
    SELECT_STRING_MULTI = "select_string_multi"
    STRING = "string"
    TEXT = "text"
    TIME = "time"

    def __str__(self) -> str:
        return str(self.value)
