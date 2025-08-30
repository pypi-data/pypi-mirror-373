from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenStackNestedSecurityGroupRulesItem")


@_attrs_define
class OpenStackNestedSecurityGroupRulesItem:
    """
    Attributes:
        id (Union[Unset, int]):
        protocol (Union[None, Unset, str]):
        from_port (Union[None, Unset, int]):
        to_port (Union[None, Unset, int]):
        cidr (Union[None, Unset, str]):
        remote_group (Union[None, Unset, str]):
        direction (Union[Unset, str]):
        ethertype (Union[Unset, str]):
        description (Union[None, Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    protocol: Union[None, Unset, str] = UNSET
    from_port: Union[None, Unset, int] = UNSET
    to_port: Union[None, Unset, int] = UNSET
    cidr: Union[None, Unset, str] = UNSET
    remote_group: Union[None, Unset, str] = UNSET
    direction: Union[Unset, str] = UNSET
    ethertype: Union[Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        protocol: Union[None, Unset, str]
        if isinstance(self.protocol, Unset):
            protocol = UNSET
        else:
            protocol = self.protocol

        from_port: Union[None, Unset, int]
        if isinstance(self.from_port, Unset):
            from_port = UNSET
        else:
            from_port = self.from_port

        to_port: Union[None, Unset, int]
        if isinstance(self.to_port, Unset):
            to_port = UNSET
        else:
            to_port = self.to_port

        cidr: Union[None, Unset, str]
        if isinstance(self.cidr, Unset):
            cidr = UNSET
        else:
            cidr = self.cidr

        remote_group: Union[None, Unset, str]
        if isinstance(self.remote_group, Unset):
            remote_group = UNSET
        else:
            remote_group = self.remote_group

        direction = self.direction

        ethertype = self.ethertype

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if from_port is not UNSET:
            field_dict["from_port"] = from_port
        if to_port is not UNSET:
            field_dict["to_port"] = to_port
        if cidr is not UNSET:
            field_dict["cidr"] = cidr
        if remote_group is not UNSET:
            field_dict["remote_group"] = remote_group
        if direction is not UNSET:
            field_dict["direction"] = direction
        if ethertype is not UNSET:
            field_dict["ethertype"] = ethertype
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        def _parse_protocol(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        protocol = _parse_protocol(d.pop("protocol", UNSET))

        def _parse_from_port(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        from_port = _parse_from_port(d.pop("from_port", UNSET))

        def _parse_to_port(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        to_port = _parse_to_port(d.pop("to_port", UNSET))

        def _parse_cidr(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cidr = _parse_cidr(d.pop("cidr", UNSET))

        def _parse_remote_group(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        remote_group = _parse_remote_group(d.pop("remote_group", UNSET))

        direction = d.pop("direction", UNSET)

        ethertype = d.pop("ethertype", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        open_stack_nested_security_group_rules_item = cls(
            id=id,
            protocol=protocol,
            from_port=from_port,
            to_port=to_port,
            cidr=cidr,
            remote_group=remote_group,
            direction=direction,
            ethertype=ethertype,
            description=description,
        )

        open_stack_nested_security_group_rules_item.additional_properties = d
        return open_stack_nested_security_group_rules_item

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
