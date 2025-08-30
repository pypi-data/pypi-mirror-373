from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedOpenStackTenantRequest")


@_attrs_define
class PatchedOpenStackTenantRequest:
    """
    Attributes:
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        availability_zone (Union[Unset, str]): Optional availability group. Will be used for all instances provisioned
            in this tenant
        default_volume_type_name (Union[Unset, str]): Volume type name to use when creating volumes.
    """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    availability_zone: Union[Unset, str] = UNSET
    default_volume_type_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        availability_zone = self.availability_zone

        default_volume_type_name = self.default_volume_type_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if availability_zone is not UNSET:
            field_dict["availability_zone"] = availability_zone
        if default_volume_type_name is not UNSET:
            field_dict["default_volume_type_name"] = default_volume_type_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        availability_zone = d.pop("availability_zone", UNSET)

        default_volume_type_name = d.pop("default_volume_type_name", UNSET)

        patched_open_stack_tenant_request = cls(
            name=name,
            description=description,
            availability_zone=availability_zone,
            default_volume_type_name=default_volume_type_name,
        )

        patched_open_stack_tenant_request.additional_properties = d
        return patched_open_stack_tenant_request

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
