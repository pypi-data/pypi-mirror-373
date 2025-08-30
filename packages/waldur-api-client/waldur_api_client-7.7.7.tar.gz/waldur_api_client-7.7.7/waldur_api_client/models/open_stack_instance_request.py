from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.open_stack_data_volume_request import OpenStackDataVolumeRequest


T = TypeVar("T", bound="OpenStackInstanceRequest")


@_attrs_define
class OpenStackInstanceRequest:
    """
    Attributes:
        name (str):
        description (Union[Unset, str]):
        system_volume_type (Union[None, Unset, str]): Volume type for the system volume
        data_volume_type (Union[None, Unset, str]): Volume type for the data volume
        data_volumes (Union[Unset, list['OpenStackDataVolumeRequest']]): Additional data volumes to attach to the
            instance
    """

    name: str
    description: Union[Unset, str] = UNSET
    system_volume_type: Union[None, Unset, str] = UNSET
    data_volume_type: Union[None, Unset, str] = UNSET
    data_volumes: Union[Unset, list["OpenStackDataVolumeRequest"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        system_volume_type: Union[None, Unset, str]
        if isinstance(self.system_volume_type, Unset):
            system_volume_type = UNSET
        else:
            system_volume_type = self.system_volume_type

        data_volume_type: Union[None, Unset, str]
        if isinstance(self.data_volume_type, Unset):
            data_volume_type = UNSET
        else:
            data_volume_type = self.data_volume_type

        data_volumes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.data_volumes, Unset):
            data_volumes = []
            for data_volumes_item_data in self.data_volumes:
                data_volumes_item = data_volumes_item_data.to_dict()
                data_volumes.append(data_volumes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if system_volume_type is not UNSET:
            field_dict["system_volume_type"] = system_volume_type
        if data_volume_type is not UNSET:
            field_dict["data_volume_type"] = data_volume_type
        if data_volumes is not UNSET:
            field_dict["data_volumes"] = data_volumes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_stack_data_volume_request import OpenStackDataVolumeRequest

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        def _parse_system_volume_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        system_volume_type = _parse_system_volume_type(d.pop("system_volume_type", UNSET))

        def _parse_data_volume_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        data_volume_type = _parse_data_volume_type(d.pop("data_volume_type", UNSET))

        data_volumes = []
        _data_volumes = d.pop("data_volumes", UNSET)
        for data_volumes_item_data in _data_volumes or []:
            data_volumes_item = OpenStackDataVolumeRequest.from_dict(data_volumes_item_data)

            data_volumes.append(data_volumes_item)

        open_stack_instance_request = cls(
            name=name,
            description=description,
            system_volume_type=system_volume_type,
            data_volume_type=data_volume_type,
            data_volumes=data_volumes,
        )

        open_stack_instance_request.additional_properties = d
        return open_stack_instance_request

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
