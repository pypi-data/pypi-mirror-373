from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenStackImage")


@_attrs_define
class OpenStackImage:
    """
    Attributes:
        url (str):
        uuid (UUID):
        name (str):
        settings (str):
        backend_id (str):
        min_disk (Union[Unset, int]): Minimum disk size in MiB
        min_ram (Union[Unset, int]): Minimum memory size in MiB
    """

    url: str
    uuid: UUID
    name: str
    settings: str
    backend_id: str
    min_disk: Union[Unset, int] = UNSET
    min_ram: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid = str(self.uuid)

        name = self.name

        settings = self.settings

        backend_id = self.backend_id

        min_disk = self.min_disk

        min_ram = self.min_ram

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "name": name,
                "settings": settings,
                "backend_id": backend_id,
            }
        )
        if min_disk is not UNSET:
            field_dict["min_disk"] = min_disk
        if min_ram is not UNSET:
            field_dict["min_ram"] = min_ram

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        name = d.pop("name")

        settings = d.pop("settings")

        backend_id = d.pop("backend_id")

        min_disk = d.pop("min_disk", UNSET)

        min_ram = d.pop("min_ram", UNSET)

        open_stack_image = cls(
            url=url,
            uuid=uuid,
            name=name,
            settings=settings,
            backend_id=backend_id,
            min_disk=min_disk,
            min_ram=min_ram,
        )

        open_stack_image.additional_properties = d
        return open_stack_image

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
