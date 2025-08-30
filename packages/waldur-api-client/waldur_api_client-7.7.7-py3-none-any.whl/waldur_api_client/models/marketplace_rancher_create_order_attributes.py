from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rancher_nested_node_request import RancherNestedNodeRequest


T = TypeVar("T", bound="MarketplaceRancherCreateOrderAttributes")


@_attrs_define
class MarketplaceRancherCreateOrderAttributes:
    """This mixin allows to specify list of fields to be rendered by serializer.
    It expects that request is available in serializer's context.

    It is disabled for nested serializers (where parent is another serializer)
    but remains active for list views (where parent is a ListSerializer).

        Attributes:
            name (str):
            nodes (list['RancherNestedNodeRequest']):
            description (Union[Unset, str]):
            tenant (Union[Unset, str]):
            ssh_public_key (Union[Unset, str]):
            install_longhorn (Union[Unset, bool]): Longhorn is a distributed block storage deployed on top of Kubernetes
                cluster Default: False.
            vm_project (Union[None, Unset, str]):
    """

    name: str
    nodes: list["RancherNestedNodeRequest"]
    description: Union[Unset, str] = UNSET
    tenant: Union[Unset, str] = UNSET
    ssh_public_key: Union[Unset, str] = UNSET
    install_longhorn: Union[Unset, bool] = False
    vm_project: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        nodes = []
        for nodes_item_data in self.nodes:
            nodes_item = nodes_item_data.to_dict()
            nodes.append(nodes_item)

        description = self.description

        tenant = self.tenant

        ssh_public_key = self.ssh_public_key

        install_longhorn = self.install_longhorn

        vm_project: Union[None, Unset, str]
        if isinstance(self.vm_project, Unset):
            vm_project = UNSET
        else:
            vm_project = self.vm_project

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "nodes": nodes,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if tenant is not UNSET:
            field_dict["tenant"] = tenant
        if ssh_public_key is not UNSET:
            field_dict["ssh_public_key"] = ssh_public_key
        if install_longhorn is not UNSET:
            field_dict["install_longhorn"] = install_longhorn
        if vm_project is not UNSET:
            field_dict["vm_project"] = vm_project

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rancher_nested_node_request import RancherNestedNodeRequest

        d = dict(src_dict)
        name = d.pop("name")

        nodes = []
        _nodes = d.pop("nodes")
        for nodes_item_data in _nodes:
            nodes_item = RancherNestedNodeRequest.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        description = d.pop("description", UNSET)

        tenant = d.pop("tenant", UNSET)

        ssh_public_key = d.pop("ssh_public_key", UNSET)

        install_longhorn = d.pop("install_longhorn", UNSET)

        def _parse_vm_project(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        vm_project = _parse_vm_project(d.pop("vm_project", UNSET))

        marketplace_rancher_create_order_attributes = cls(
            name=name,
            nodes=nodes,
            description=description,
            tenant=tenant,
            ssh_public_key=ssh_public_key,
            install_longhorn=install_longhorn,
            vm_project=vm_project,
        )

        marketplace_rancher_create_order_attributes.additional_properties = d
        return marketplace_rancher_create_order_attributes

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
