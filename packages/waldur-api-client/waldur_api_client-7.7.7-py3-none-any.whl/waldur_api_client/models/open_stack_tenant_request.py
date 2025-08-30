from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenStackTenantRequest")


@_attrs_define
class OpenStackTenantRequest:
    """
    Attributes:
        name (str):
        service_settings (str):
        project (str):
        description (Union[Unset, str]):
        availability_zone (Union[Unset, str]): Optional availability group. Will be used for all instances provisioned
            in this tenant
        subnet_cidr (Union[Unset, str]):  Default: '192.168.42.0/24'.
        default_volume_type_name (Union[Unset, str]): Volume type name to use when creating volumes.
    """

    name: str
    service_settings: str
    project: str
    description: Union[Unset, str] = UNSET
    availability_zone: Union[Unset, str] = UNSET
    subnet_cidr: Union[Unset, str] = "192.168.42.0/24"
    default_volume_type_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        service_settings = self.service_settings

        project = self.project

        description = self.description

        availability_zone = self.availability_zone

        subnet_cidr = self.subnet_cidr

        default_volume_type_name = self.default_volume_type_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "service_settings": service_settings,
                "project": project,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if availability_zone is not UNSET:
            field_dict["availability_zone"] = availability_zone
        if subnet_cidr is not UNSET:
            field_dict["subnet_cidr"] = subnet_cidr
        if default_volume_type_name is not UNSET:
            field_dict["default_volume_type_name"] = default_volume_type_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        service_settings = d.pop("service_settings")

        project = d.pop("project")

        description = d.pop("description", UNSET)

        availability_zone = d.pop("availability_zone", UNSET)

        subnet_cidr = d.pop("subnet_cidr", UNSET)

        default_volume_type_name = d.pop("default_volume_type_name", UNSET)

        open_stack_tenant_request = cls(
            name=name,
            service_settings=service_settings,
            project=project,
            description=description,
            availability_zone=availability_zone,
            subnet_cidr=subnet_cidr,
            default_volume_type_name=default_volume_type_name,
        )

        open_stack_tenant_request.additional_properties = d
        return open_stack_tenant_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
