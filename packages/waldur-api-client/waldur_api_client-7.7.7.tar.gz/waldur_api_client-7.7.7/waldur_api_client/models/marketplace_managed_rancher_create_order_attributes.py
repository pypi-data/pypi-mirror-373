from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MarketplaceManagedRancherCreateOrderAttributes")


@_attrs_define
class MarketplaceManagedRancherCreateOrderAttributes:
    """
    Attributes:
        name (str): Unique identifier for the cluster
        worker_nodes_count (int):
        worker_nodes_flavor_name (str):
        worker_nodes_data_volume_size (int): Data volume size for worker nodes in MB (consistent with OpenStack)
        worker_nodes_data_volume_type_name (Union[Unset, str]):
        openstack_offering_uuid_list (Union[Unset, list[UUID]]): List of UUID of OpenStack offerings where tenant can be
            created
        install_longhorn (Union[Unset, bool]): Longhorn is a distributed block storage deployed on top of Kubernetes
            cluster Default: False.
        worker_nodes_longhorn_volume_size (Union[Unset, int]): Longhorn storage volume size for worker nodes in MB
            (consistent with OpenStack)
        worker_nodes_longhorn_volume_type_name (Union[Unset, str]):
    """

    name: str
    worker_nodes_count: int
    worker_nodes_flavor_name: str
    worker_nodes_data_volume_size: int
    worker_nodes_data_volume_type_name: Union[Unset, str] = UNSET
    openstack_offering_uuid_list: Union[Unset, list[UUID]] = UNSET
    install_longhorn: Union[Unset, bool] = False
    worker_nodes_longhorn_volume_size: Union[Unset, int] = UNSET
    worker_nodes_longhorn_volume_type_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        worker_nodes_count = self.worker_nodes_count

        worker_nodes_flavor_name = self.worker_nodes_flavor_name

        worker_nodes_data_volume_size = self.worker_nodes_data_volume_size

        worker_nodes_data_volume_type_name = self.worker_nodes_data_volume_type_name

        openstack_offering_uuid_list: Union[Unset, list[str]] = UNSET
        if not isinstance(self.openstack_offering_uuid_list, Unset):
            openstack_offering_uuid_list = []
            for openstack_offering_uuid_list_item_data in self.openstack_offering_uuid_list:
                openstack_offering_uuid_list_item = str(openstack_offering_uuid_list_item_data)
                openstack_offering_uuid_list.append(openstack_offering_uuid_list_item)

        install_longhorn = self.install_longhorn

        worker_nodes_longhorn_volume_size = self.worker_nodes_longhorn_volume_size

        worker_nodes_longhorn_volume_type_name = self.worker_nodes_longhorn_volume_type_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "worker_nodes_count": worker_nodes_count,
                "worker_nodes_flavor_name": worker_nodes_flavor_name,
                "worker_nodes_data_volume_size": worker_nodes_data_volume_size,
            }
        )
        if worker_nodes_data_volume_type_name is not UNSET:
            field_dict["worker_nodes_data_volume_type_name"] = worker_nodes_data_volume_type_name
        if openstack_offering_uuid_list is not UNSET:
            field_dict["openstack_offering_uuid_list"] = openstack_offering_uuid_list
        if install_longhorn is not UNSET:
            field_dict["install_longhorn"] = install_longhorn
        if worker_nodes_longhorn_volume_size is not UNSET:
            field_dict["worker_nodes_longhorn_volume_size"] = worker_nodes_longhorn_volume_size
        if worker_nodes_longhorn_volume_type_name is not UNSET:
            field_dict["worker_nodes_longhorn_volume_type_name"] = worker_nodes_longhorn_volume_type_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        worker_nodes_count = d.pop("worker_nodes_count")

        worker_nodes_flavor_name = d.pop("worker_nodes_flavor_name")

        worker_nodes_data_volume_size = d.pop("worker_nodes_data_volume_size")

        worker_nodes_data_volume_type_name = d.pop("worker_nodes_data_volume_type_name", UNSET)

        openstack_offering_uuid_list = []
        _openstack_offering_uuid_list = d.pop("openstack_offering_uuid_list", UNSET)
        for openstack_offering_uuid_list_item_data in _openstack_offering_uuid_list or []:
            openstack_offering_uuid_list_item = UUID(openstack_offering_uuid_list_item_data)

            openstack_offering_uuid_list.append(openstack_offering_uuid_list_item)

        install_longhorn = d.pop("install_longhorn", UNSET)

        worker_nodes_longhorn_volume_size = d.pop("worker_nodes_longhorn_volume_size", UNSET)

        worker_nodes_longhorn_volume_type_name = d.pop("worker_nodes_longhorn_volume_type_name", UNSET)

        marketplace_managed_rancher_create_order_attributes = cls(
            name=name,
            worker_nodes_count=worker_nodes_count,
            worker_nodes_flavor_name=worker_nodes_flavor_name,
            worker_nodes_data_volume_size=worker_nodes_data_volume_size,
            worker_nodes_data_volume_type_name=worker_nodes_data_volume_type_name,
            openstack_offering_uuid_list=openstack_offering_uuid_list,
            install_longhorn=install_longhorn,
            worker_nodes_longhorn_volume_size=worker_nodes_longhorn_volume_size,
            worker_nodes_longhorn_volume_type_name=worker_nodes_longhorn_volume_type_name,
        )

        marketplace_managed_rancher_create_order_attributes.additional_properties = d
        return marketplace_managed_rancher_create_order_attributes

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
