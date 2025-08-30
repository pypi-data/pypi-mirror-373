from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OfferingUserRole")


@_attrs_define
class OfferingUserRole:
    """
    Attributes:
        name (str):
        uuid (UUID):
        offering (str):
        offering_uuid (UUID):
        offering_name (str):
    """

    name: str
    uuid: UUID
    offering: str
    offering_uuid: UUID
    offering_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        uuid = str(self.uuid)

        offering = self.offering

        offering_uuid = str(self.offering_uuid)

        offering_name = self.offering_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "uuid": uuid,
                "offering": offering,
                "offering_uuid": offering_uuid,
                "offering_name": offering_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        uuid = UUID(d.pop("uuid"))

        offering = d.pop("offering")

        offering_uuid = UUID(d.pop("offering_uuid"))

        offering_name = d.pop("offering_name")

        offering_user_role = cls(
            name=name,
            uuid=uuid,
            offering=offering,
            offering_uuid=offering_uuid,
            offering_name=offering_name,
        )

        offering_user_role.additional_properties = d
        return offering_user_role

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
