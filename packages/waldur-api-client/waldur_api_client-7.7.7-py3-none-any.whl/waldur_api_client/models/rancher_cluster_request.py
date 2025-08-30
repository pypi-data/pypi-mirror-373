from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rancher_nested_node_request import RancherNestedNodeRequest


T = TypeVar("T", bound="RancherClusterRequest")


@_attrs_define
class RancherClusterRequest:
    """
    Attributes:
        name (str):
        service_settings (str):
        project (str):
        nodes (list['RancherNestedNodeRequest']):
        description (Union[Unset, str]):
        tenant (Union[Unset, str]):
        vm_project (Union[None, Unset, str]):
        ssh_public_key (Union[Unset, str]):
        install_longhorn (Union[Unset, bool]): Longhorn is a distributed block storage deployed on top of Kubernetes
            cluster Default: False.
    """

    name: str
    service_settings: str
    project: str
    nodes: list["RancherNestedNodeRequest"]
    description: Union[Unset, str] = UNSET
    tenant: Union[Unset, str] = UNSET
    vm_project: Union[None, Unset, str] = UNSET
    ssh_public_key: Union[Unset, str] = UNSET
    install_longhorn: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        service_settings = self.service_settings

        project = self.project

        nodes = []
        for nodes_item_data in self.nodes:
            nodes_item = nodes_item_data.to_dict()
            nodes.append(nodes_item)

        description = self.description

        tenant = self.tenant

        vm_project: Union[None, Unset, str]
        if isinstance(self.vm_project, Unset):
            vm_project = UNSET
        else:
            vm_project = self.vm_project

        ssh_public_key = self.ssh_public_key

        install_longhorn = self.install_longhorn

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "service_settings": service_settings,
                "project": project,
                "nodes": nodes,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if tenant is not UNSET:
            field_dict["tenant"] = tenant
        if vm_project is not UNSET:
            field_dict["vm_project"] = vm_project
        if ssh_public_key is not UNSET:
            field_dict["ssh_public_key"] = ssh_public_key
        if install_longhorn is not UNSET:
            field_dict["install_longhorn"] = install_longhorn

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rancher_nested_node_request import RancherNestedNodeRequest

        d = dict(src_dict)
        name = d.pop("name")

        service_settings = d.pop("service_settings")

        project = d.pop("project")

        nodes = []
        _nodes = d.pop("nodes")
        for nodes_item_data in _nodes:
            nodes_item = RancherNestedNodeRequest.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        description = d.pop("description", UNSET)

        tenant = d.pop("tenant", UNSET)

        def _parse_vm_project(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        vm_project = _parse_vm_project(d.pop("vm_project", UNSET))

        ssh_public_key = d.pop("ssh_public_key", UNSET)

        install_longhorn = d.pop("install_longhorn", UNSET)

        rancher_cluster_request = cls(
            name=name,
            service_settings=service_settings,
            project=project,
            nodes=nodes,
            description=description,
            tenant=tenant,
            vm_project=vm_project,
            ssh_public_key=ssh_public_key,
            install_longhorn=install_longhorn,
        )

        rancher_cluster_request.additional_properties = d
        return rancher_cluster_request

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
