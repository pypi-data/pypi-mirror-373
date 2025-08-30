import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.account_name_generation_policy_enum import AccountNameGenerationPolicyEnum
from ..models.storage_mode_enum import StorageModeEnum
from ..models.username_generation_policy_enum import UsernameGenerationPolicyEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="MergedPluginOptionsRequest")


@_attrs_define
class MergedPluginOptionsRequest:
    """
    Attributes:
        auto_approve_remote_orders (Union[Unset, bool]): If set to True, an order can be processed without approval
        service_provider_can_create_offering_user (Union[Unset, bool]): Service provider can create offering user
        max_resource_termination_offset_in_days (Union[Unset, int]): Maximum resource termination offset in days
        default_resource_termination_offset_in_days (Union[Unset, int]): If set, it will be used as a default resource
            termination offset in days
        is_resource_termination_date_required (Union[Unset, bool]): If set to True, resource termination date is
            required
        latest_date_for_resource_termination (Union[Unset, datetime.date]): If set, it will be used as a latest date for
            resource termination
        auto_approve_in_service_provider_projects (Union[Unset, bool]): Skip approval of public offering belonging to
            the same organization under which the request is done
        supports_downscaling (Union[Unset, bool]): If set to True, it will be possible to downscale resources
        supports_pausing (Union[Unset, bool]): If set to True, it will be possible to pause resources
        minimal_team_count_for_provisioning (Union[Unset, int]): Minimal team count required for provisioning of
            resources
        required_team_role_for_provisioning (Union[Unset, str]): Required user role in a project for provisioning of
            resources
        default_internal_network_mtu (Union[Unset, int]): If set, it will be used as a default MTU for the first network
            in a tenant
        max_instances (Union[Unset, int]): Default limit for number of instances in OpenStack tenant
        max_volumes (Union[Unset, int]): Default limit for number of volumes in OpenStack tenant
        storage_mode (Union[Unset, StorageModeEnum]):
        snapshot_size_limit_gb (Union[Unset, int]): Default limit for snapshot size in GB
        heappe_cluster_id (Union[Unset, str]): HEAppE cluster id
        heappe_local_base_path (Union[Unset, str]): HEAppE local base path
        heappe_url (Union[Unset, str]): HEAppE url
        heappe_username (Union[Unset, str]): HEAppE username
        homedir_prefix (Union[Unset, str]): GLAuth homedir prefix Default: '/home/'.
        initial_primarygroup_number (Union[Unset, int]): GLAuth initial primary group number Default: 5000.
        initial_uidnumber (Union[Unset, int]): GLAuth initial uidnumber Default: 5000.
        initial_usergroup_number (Union[Unset, int]): GLAuth initial usergroup number Default: 6000.
        username_anonymized_prefix (Union[Unset, str]): GLAuth prefix for anonymized usernames Default: 'waldur_'.
        username_generation_policy (Union[Unset, UsernameGenerationPolicyEnum]):  Default:
            UsernameGenerationPolicyEnum.SERVICE_PROVIDER.
        enable_issues_for_membership_changes (Union[Unset, bool]): Enable issues for membership changes
        flavors_regex (Union[Unset, str]): Regular expression to limit flavors list
        openstack_offering_uuid_list (Union[Unset, list[str]]): List of UUID of OpenStack offerings where tenant can be
            created
        managed_rancher_server_flavor_name (Union[Unset, str]):
        managed_rancher_server_system_volume_size_gb (Union[Unset, int]):
        managed_rancher_server_system_volume_type_name (Union[Unset, str]):
        managed_rancher_server_data_volume_size_gb (Union[Unset, int]):
        managed_rancher_server_data_volume_type_name (Union[Unset, str]):
        managed_rancher_worker_system_volume_size_gb (Union[Unset, int]):
        managed_rancher_worker_system_volume_type_name (Union[Unset, str]):
        managed_rancher_load_balancer_flavor_name (Union[Unset, str]):
        managed_rancher_load_balancer_system_volume_size_gb (Union[Unset, int]):
        managed_rancher_load_balancer_system_volume_type_name (Union[Unset, str]):
        managed_rancher_load_balancer_data_volume_size_gb (Union[Unset, int]):
        managed_rancher_load_balancer_data_volume_type_name (Union[Unset, str]):
        managed_rancher_tenant_max_cpu (Union[Unset, int]): Max number of vCPUs for tenants
        managed_rancher_tenant_max_ram (Union[Unset, int]): Max number of RAM for tenants (GB)
        managed_rancher_tenant_max_disk (Union[Unset, int]): Max size of disk space for tenants (GB)
        account_name_generation_policy (Union[AccountNameGenerationPolicyEnum, None, Unset]): Slurm account name
            generation policy
    """

    auto_approve_remote_orders: Union[Unset, bool] = UNSET
    service_provider_can_create_offering_user: Union[Unset, bool] = UNSET
    max_resource_termination_offset_in_days: Union[Unset, int] = UNSET
    default_resource_termination_offset_in_days: Union[Unset, int] = UNSET
    is_resource_termination_date_required: Union[Unset, bool] = UNSET
    latest_date_for_resource_termination: Union[Unset, datetime.date] = UNSET
    auto_approve_in_service_provider_projects: Union[Unset, bool] = UNSET
    supports_downscaling: Union[Unset, bool] = UNSET
    supports_pausing: Union[Unset, bool] = UNSET
    minimal_team_count_for_provisioning: Union[Unset, int] = UNSET
    required_team_role_for_provisioning: Union[Unset, str] = UNSET
    default_internal_network_mtu: Union[Unset, int] = UNSET
    max_instances: Union[Unset, int] = UNSET
    max_volumes: Union[Unset, int] = UNSET
    storage_mode: Union[Unset, StorageModeEnum] = UNSET
    snapshot_size_limit_gb: Union[Unset, int] = UNSET
    heappe_cluster_id: Union[Unset, str] = UNSET
    heappe_local_base_path: Union[Unset, str] = UNSET
    heappe_url: Union[Unset, str] = UNSET
    heappe_username: Union[Unset, str] = UNSET
    homedir_prefix: Union[Unset, str] = "/home/"
    initial_primarygroup_number: Union[Unset, int] = 5000
    initial_uidnumber: Union[Unset, int] = 5000
    initial_usergroup_number: Union[Unset, int] = 6000
    username_anonymized_prefix: Union[Unset, str] = "waldur_"
    username_generation_policy: Union[Unset, UsernameGenerationPolicyEnum] = (
        UsernameGenerationPolicyEnum.SERVICE_PROVIDER
    )
    enable_issues_for_membership_changes: Union[Unset, bool] = UNSET
    flavors_regex: Union[Unset, str] = UNSET
    openstack_offering_uuid_list: Union[Unset, list[str]] = UNSET
    managed_rancher_server_flavor_name: Union[Unset, str] = UNSET
    managed_rancher_server_system_volume_size_gb: Union[Unset, int] = UNSET
    managed_rancher_server_system_volume_type_name: Union[Unset, str] = UNSET
    managed_rancher_server_data_volume_size_gb: Union[Unset, int] = UNSET
    managed_rancher_server_data_volume_type_name: Union[Unset, str] = UNSET
    managed_rancher_worker_system_volume_size_gb: Union[Unset, int] = UNSET
    managed_rancher_worker_system_volume_type_name: Union[Unset, str] = UNSET
    managed_rancher_load_balancer_flavor_name: Union[Unset, str] = UNSET
    managed_rancher_load_balancer_system_volume_size_gb: Union[Unset, int] = UNSET
    managed_rancher_load_balancer_system_volume_type_name: Union[Unset, str] = UNSET
    managed_rancher_load_balancer_data_volume_size_gb: Union[Unset, int] = UNSET
    managed_rancher_load_balancer_data_volume_type_name: Union[Unset, str] = UNSET
    managed_rancher_tenant_max_cpu: Union[Unset, int] = UNSET
    managed_rancher_tenant_max_ram: Union[Unset, int] = UNSET
    managed_rancher_tenant_max_disk: Union[Unset, int] = UNSET
    account_name_generation_policy: Union[AccountNameGenerationPolicyEnum, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        auto_approve_remote_orders = self.auto_approve_remote_orders

        service_provider_can_create_offering_user = self.service_provider_can_create_offering_user

        max_resource_termination_offset_in_days = self.max_resource_termination_offset_in_days

        default_resource_termination_offset_in_days = self.default_resource_termination_offset_in_days

        is_resource_termination_date_required = self.is_resource_termination_date_required

        latest_date_for_resource_termination: Union[Unset, str] = UNSET
        if not isinstance(self.latest_date_for_resource_termination, Unset):
            latest_date_for_resource_termination = self.latest_date_for_resource_termination.isoformat()

        auto_approve_in_service_provider_projects = self.auto_approve_in_service_provider_projects

        supports_downscaling = self.supports_downscaling

        supports_pausing = self.supports_pausing

        minimal_team_count_for_provisioning = self.minimal_team_count_for_provisioning

        required_team_role_for_provisioning = self.required_team_role_for_provisioning

        default_internal_network_mtu = self.default_internal_network_mtu

        max_instances = self.max_instances

        max_volumes = self.max_volumes

        storage_mode: Union[Unset, str] = UNSET
        if not isinstance(self.storage_mode, Unset):
            storage_mode = self.storage_mode.value

        snapshot_size_limit_gb = self.snapshot_size_limit_gb

        heappe_cluster_id = self.heappe_cluster_id

        heappe_local_base_path = self.heappe_local_base_path

        heappe_url = self.heappe_url

        heappe_username = self.heappe_username

        homedir_prefix = self.homedir_prefix

        initial_primarygroup_number = self.initial_primarygroup_number

        initial_uidnumber = self.initial_uidnumber

        initial_usergroup_number = self.initial_usergroup_number

        username_anonymized_prefix = self.username_anonymized_prefix

        username_generation_policy: Union[Unset, str] = UNSET
        if not isinstance(self.username_generation_policy, Unset):
            username_generation_policy = self.username_generation_policy.value

        enable_issues_for_membership_changes = self.enable_issues_for_membership_changes

        flavors_regex = self.flavors_regex

        openstack_offering_uuid_list: Union[Unset, list[str]] = UNSET
        if not isinstance(self.openstack_offering_uuid_list, Unset):
            openstack_offering_uuid_list = self.openstack_offering_uuid_list

        managed_rancher_server_flavor_name = self.managed_rancher_server_flavor_name

        managed_rancher_server_system_volume_size_gb = self.managed_rancher_server_system_volume_size_gb

        managed_rancher_server_system_volume_type_name = self.managed_rancher_server_system_volume_type_name

        managed_rancher_server_data_volume_size_gb = self.managed_rancher_server_data_volume_size_gb

        managed_rancher_server_data_volume_type_name = self.managed_rancher_server_data_volume_type_name

        managed_rancher_worker_system_volume_size_gb = self.managed_rancher_worker_system_volume_size_gb

        managed_rancher_worker_system_volume_type_name = self.managed_rancher_worker_system_volume_type_name

        managed_rancher_load_balancer_flavor_name = self.managed_rancher_load_balancer_flavor_name

        managed_rancher_load_balancer_system_volume_size_gb = self.managed_rancher_load_balancer_system_volume_size_gb

        managed_rancher_load_balancer_system_volume_type_name = (
            self.managed_rancher_load_balancer_system_volume_type_name
        )

        managed_rancher_load_balancer_data_volume_size_gb = self.managed_rancher_load_balancer_data_volume_size_gb

        managed_rancher_load_balancer_data_volume_type_name = self.managed_rancher_load_balancer_data_volume_type_name

        managed_rancher_tenant_max_cpu = self.managed_rancher_tenant_max_cpu

        managed_rancher_tenant_max_ram = self.managed_rancher_tenant_max_ram

        managed_rancher_tenant_max_disk = self.managed_rancher_tenant_max_disk

        account_name_generation_policy: Union[None, Unset, str]
        if isinstance(self.account_name_generation_policy, Unset):
            account_name_generation_policy = UNSET
        elif isinstance(self.account_name_generation_policy, AccountNameGenerationPolicyEnum):
            account_name_generation_policy = self.account_name_generation_policy.value
        else:
            account_name_generation_policy = self.account_name_generation_policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if auto_approve_remote_orders is not UNSET:
            field_dict["auto_approve_remote_orders"] = auto_approve_remote_orders
        if service_provider_can_create_offering_user is not UNSET:
            field_dict["service_provider_can_create_offering_user"] = service_provider_can_create_offering_user
        if max_resource_termination_offset_in_days is not UNSET:
            field_dict["max_resource_termination_offset_in_days"] = max_resource_termination_offset_in_days
        if default_resource_termination_offset_in_days is not UNSET:
            field_dict["default_resource_termination_offset_in_days"] = default_resource_termination_offset_in_days
        if is_resource_termination_date_required is not UNSET:
            field_dict["is_resource_termination_date_required"] = is_resource_termination_date_required
        if latest_date_for_resource_termination is not UNSET:
            field_dict["latest_date_for_resource_termination"] = latest_date_for_resource_termination
        if auto_approve_in_service_provider_projects is not UNSET:
            field_dict["auto_approve_in_service_provider_projects"] = auto_approve_in_service_provider_projects
        if supports_downscaling is not UNSET:
            field_dict["supports_downscaling"] = supports_downscaling
        if supports_pausing is not UNSET:
            field_dict["supports_pausing"] = supports_pausing
        if minimal_team_count_for_provisioning is not UNSET:
            field_dict["minimal_team_count_for_provisioning"] = minimal_team_count_for_provisioning
        if required_team_role_for_provisioning is not UNSET:
            field_dict["required_team_role_for_provisioning"] = required_team_role_for_provisioning
        if default_internal_network_mtu is not UNSET:
            field_dict["default_internal_network_mtu"] = default_internal_network_mtu
        if max_instances is not UNSET:
            field_dict["max_instances"] = max_instances
        if max_volumes is not UNSET:
            field_dict["max_volumes"] = max_volumes
        if storage_mode is not UNSET:
            field_dict["storage_mode"] = storage_mode
        if snapshot_size_limit_gb is not UNSET:
            field_dict["snapshot_size_limit_gb"] = snapshot_size_limit_gb
        if heappe_cluster_id is not UNSET:
            field_dict["heappe_cluster_id"] = heappe_cluster_id
        if heappe_local_base_path is not UNSET:
            field_dict["heappe_local_base_path"] = heappe_local_base_path
        if heappe_url is not UNSET:
            field_dict["heappe_url"] = heappe_url
        if heappe_username is not UNSET:
            field_dict["heappe_username"] = heappe_username
        if homedir_prefix is not UNSET:
            field_dict["homedir_prefix"] = homedir_prefix
        if initial_primarygroup_number is not UNSET:
            field_dict["initial_primarygroup_number"] = initial_primarygroup_number
        if initial_uidnumber is not UNSET:
            field_dict["initial_uidnumber"] = initial_uidnumber
        if initial_usergroup_number is not UNSET:
            field_dict["initial_usergroup_number"] = initial_usergroup_number
        if username_anonymized_prefix is not UNSET:
            field_dict["username_anonymized_prefix"] = username_anonymized_prefix
        if username_generation_policy is not UNSET:
            field_dict["username_generation_policy"] = username_generation_policy
        if enable_issues_for_membership_changes is not UNSET:
            field_dict["enable_issues_for_membership_changes"] = enable_issues_for_membership_changes
        if flavors_regex is not UNSET:
            field_dict["flavors_regex"] = flavors_regex
        if openstack_offering_uuid_list is not UNSET:
            field_dict["openstack_offering_uuid_list"] = openstack_offering_uuid_list
        if managed_rancher_server_flavor_name is not UNSET:
            field_dict["managed_rancher_server_flavor_name"] = managed_rancher_server_flavor_name
        if managed_rancher_server_system_volume_size_gb is not UNSET:
            field_dict["managed_rancher_server_system_volume_size_gb"] = managed_rancher_server_system_volume_size_gb
        if managed_rancher_server_system_volume_type_name is not UNSET:
            field_dict["managed_rancher_server_system_volume_type_name"] = (
                managed_rancher_server_system_volume_type_name
            )
        if managed_rancher_server_data_volume_size_gb is not UNSET:
            field_dict["managed_rancher_server_data_volume_size_gb"] = managed_rancher_server_data_volume_size_gb
        if managed_rancher_server_data_volume_type_name is not UNSET:
            field_dict["managed_rancher_server_data_volume_type_name"] = managed_rancher_server_data_volume_type_name
        if managed_rancher_worker_system_volume_size_gb is not UNSET:
            field_dict["managed_rancher_worker_system_volume_size_gb"] = managed_rancher_worker_system_volume_size_gb
        if managed_rancher_worker_system_volume_type_name is not UNSET:
            field_dict["managed_rancher_worker_system_volume_type_name"] = (
                managed_rancher_worker_system_volume_type_name
            )
        if managed_rancher_load_balancer_flavor_name is not UNSET:
            field_dict["managed_rancher_load_balancer_flavor_name"] = managed_rancher_load_balancer_flavor_name
        if managed_rancher_load_balancer_system_volume_size_gb is not UNSET:
            field_dict["managed_rancher_load_balancer_system_volume_size_gb"] = (
                managed_rancher_load_balancer_system_volume_size_gb
            )
        if managed_rancher_load_balancer_system_volume_type_name is not UNSET:
            field_dict["managed_rancher_load_balancer_system_volume_type_name"] = (
                managed_rancher_load_balancer_system_volume_type_name
            )
        if managed_rancher_load_balancer_data_volume_size_gb is not UNSET:
            field_dict["managed_rancher_load_balancer_data_volume_size_gb"] = (
                managed_rancher_load_balancer_data_volume_size_gb
            )
        if managed_rancher_load_balancer_data_volume_type_name is not UNSET:
            field_dict["managed_rancher_load_balancer_data_volume_type_name"] = (
                managed_rancher_load_balancer_data_volume_type_name
            )
        if managed_rancher_tenant_max_cpu is not UNSET:
            field_dict["managed_rancher_tenant_max_cpu"] = managed_rancher_tenant_max_cpu
        if managed_rancher_tenant_max_ram is not UNSET:
            field_dict["managed_rancher_tenant_max_ram"] = managed_rancher_tenant_max_ram
        if managed_rancher_tenant_max_disk is not UNSET:
            field_dict["managed_rancher_tenant_max_disk"] = managed_rancher_tenant_max_disk
        if account_name_generation_policy is not UNSET:
            field_dict["account_name_generation_policy"] = account_name_generation_policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        auto_approve_remote_orders = d.pop("auto_approve_remote_orders", UNSET)

        service_provider_can_create_offering_user = d.pop("service_provider_can_create_offering_user", UNSET)

        max_resource_termination_offset_in_days = d.pop("max_resource_termination_offset_in_days", UNSET)

        default_resource_termination_offset_in_days = d.pop("default_resource_termination_offset_in_days", UNSET)

        is_resource_termination_date_required = d.pop("is_resource_termination_date_required", UNSET)

        _latest_date_for_resource_termination = d.pop("latest_date_for_resource_termination", UNSET)
        latest_date_for_resource_termination: Union[Unset, datetime.date]
        if isinstance(_latest_date_for_resource_termination, Unset):
            latest_date_for_resource_termination = UNSET
        else:
            latest_date_for_resource_termination = isoparse(_latest_date_for_resource_termination).date()

        auto_approve_in_service_provider_projects = d.pop("auto_approve_in_service_provider_projects", UNSET)

        supports_downscaling = d.pop("supports_downscaling", UNSET)

        supports_pausing = d.pop("supports_pausing", UNSET)

        minimal_team_count_for_provisioning = d.pop("minimal_team_count_for_provisioning", UNSET)

        required_team_role_for_provisioning = d.pop("required_team_role_for_provisioning", UNSET)

        default_internal_network_mtu = d.pop("default_internal_network_mtu", UNSET)

        max_instances = d.pop("max_instances", UNSET)

        max_volumes = d.pop("max_volumes", UNSET)

        _storage_mode = d.pop("storage_mode", UNSET)
        storage_mode: Union[Unset, StorageModeEnum]
        if isinstance(_storage_mode, Unset):
            storage_mode = UNSET
        else:
            storage_mode = StorageModeEnum(_storage_mode)

        snapshot_size_limit_gb = d.pop("snapshot_size_limit_gb", UNSET)

        heappe_cluster_id = d.pop("heappe_cluster_id", UNSET)

        heappe_local_base_path = d.pop("heappe_local_base_path", UNSET)

        heappe_url = d.pop("heappe_url", UNSET)

        heappe_username = d.pop("heappe_username", UNSET)

        homedir_prefix = d.pop("homedir_prefix", UNSET)

        initial_primarygroup_number = d.pop("initial_primarygroup_number", UNSET)

        initial_uidnumber = d.pop("initial_uidnumber", UNSET)

        initial_usergroup_number = d.pop("initial_usergroup_number", UNSET)

        username_anonymized_prefix = d.pop("username_anonymized_prefix", UNSET)

        _username_generation_policy = d.pop("username_generation_policy", UNSET)
        username_generation_policy: Union[Unset, UsernameGenerationPolicyEnum]
        if isinstance(_username_generation_policy, Unset):
            username_generation_policy = UNSET
        else:
            username_generation_policy = UsernameGenerationPolicyEnum(_username_generation_policy)

        enable_issues_for_membership_changes = d.pop("enable_issues_for_membership_changes", UNSET)

        flavors_regex = d.pop("flavors_regex", UNSET)

        openstack_offering_uuid_list = cast(list[str], d.pop("openstack_offering_uuid_list", UNSET))

        managed_rancher_server_flavor_name = d.pop("managed_rancher_server_flavor_name", UNSET)

        managed_rancher_server_system_volume_size_gb = d.pop("managed_rancher_server_system_volume_size_gb", UNSET)

        managed_rancher_server_system_volume_type_name = d.pop("managed_rancher_server_system_volume_type_name", UNSET)

        managed_rancher_server_data_volume_size_gb = d.pop("managed_rancher_server_data_volume_size_gb", UNSET)

        managed_rancher_server_data_volume_type_name = d.pop("managed_rancher_server_data_volume_type_name", UNSET)

        managed_rancher_worker_system_volume_size_gb = d.pop("managed_rancher_worker_system_volume_size_gb", UNSET)

        managed_rancher_worker_system_volume_type_name = d.pop("managed_rancher_worker_system_volume_type_name", UNSET)

        managed_rancher_load_balancer_flavor_name = d.pop("managed_rancher_load_balancer_flavor_name", UNSET)

        managed_rancher_load_balancer_system_volume_size_gb = d.pop(
            "managed_rancher_load_balancer_system_volume_size_gb", UNSET
        )

        managed_rancher_load_balancer_system_volume_type_name = d.pop(
            "managed_rancher_load_balancer_system_volume_type_name", UNSET
        )

        managed_rancher_load_balancer_data_volume_size_gb = d.pop(
            "managed_rancher_load_balancer_data_volume_size_gb", UNSET
        )

        managed_rancher_load_balancer_data_volume_type_name = d.pop(
            "managed_rancher_load_balancer_data_volume_type_name", UNSET
        )

        managed_rancher_tenant_max_cpu = d.pop("managed_rancher_tenant_max_cpu", UNSET)

        managed_rancher_tenant_max_ram = d.pop("managed_rancher_tenant_max_ram", UNSET)

        managed_rancher_tenant_max_disk = d.pop("managed_rancher_tenant_max_disk", UNSET)

        def _parse_account_name_generation_policy(data: object) -> Union[AccountNameGenerationPolicyEnum, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                account_name_generation_policy_type_0 = AccountNameGenerationPolicyEnum(data)

                return account_name_generation_policy_type_0
            except:  # noqa: E722
                pass
            return cast(Union[AccountNameGenerationPolicyEnum, None, Unset], data)

        account_name_generation_policy = _parse_account_name_generation_policy(
            d.pop("account_name_generation_policy", UNSET)
        )

        merged_plugin_options_request = cls(
            auto_approve_remote_orders=auto_approve_remote_orders,
            service_provider_can_create_offering_user=service_provider_can_create_offering_user,
            max_resource_termination_offset_in_days=max_resource_termination_offset_in_days,
            default_resource_termination_offset_in_days=default_resource_termination_offset_in_days,
            is_resource_termination_date_required=is_resource_termination_date_required,
            latest_date_for_resource_termination=latest_date_for_resource_termination,
            auto_approve_in_service_provider_projects=auto_approve_in_service_provider_projects,
            supports_downscaling=supports_downscaling,
            supports_pausing=supports_pausing,
            minimal_team_count_for_provisioning=minimal_team_count_for_provisioning,
            required_team_role_for_provisioning=required_team_role_for_provisioning,
            default_internal_network_mtu=default_internal_network_mtu,
            max_instances=max_instances,
            max_volumes=max_volumes,
            storage_mode=storage_mode,
            snapshot_size_limit_gb=snapshot_size_limit_gb,
            heappe_cluster_id=heappe_cluster_id,
            heappe_local_base_path=heappe_local_base_path,
            heappe_url=heappe_url,
            heappe_username=heappe_username,
            homedir_prefix=homedir_prefix,
            initial_primarygroup_number=initial_primarygroup_number,
            initial_uidnumber=initial_uidnumber,
            initial_usergroup_number=initial_usergroup_number,
            username_anonymized_prefix=username_anonymized_prefix,
            username_generation_policy=username_generation_policy,
            enable_issues_for_membership_changes=enable_issues_for_membership_changes,
            flavors_regex=flavors_regex,
            openstack_offering_uuid_list=openstack_offering_uuid_list,
            managed_rancher_server_flavor_name=managed_rancher_server_flavor_name,
            managed_rancher_server_system_volume_size_gb=managed_rancher_server_system_volume_size_gb,
            managed_rancher_server_system_volume_type_name=managed_rancher_server_system_volume_type_name,
            managed_rancher_server_data_volume_size_gb=managed_rancher_server_data_volume_size_gb,
            managed_rancher_server_data_volume_type_name=managed_rancher_server_data_volume_type_name,
            managed_rancher_worker_system_volume_size_gb=managed_rancher_worker_system_volume_size_gb,
            managed_rancher_worker_system_volume_type_name=managed_rancher_worker_system_volume_type_name,
            managed_rancher_load_balancer_flavor_name=managed_rancher_load_balancer_flavor_name,
            managed_rancher_load_balancer_system_volume_size_gb=managed_rancher_load_balancer_system_volume_size_gb,
            managed_rancher_load_balancer_system_volume_type_name=managed_rancher_load_balancer_system_volume_type_name,
            managed_rancher_load_balancer_data_volume_size_gb=managed_rancher_load_balancer_data_volume_size_gb,
            managed_rancher_load_balancer_data_volume_type_name=managed_rancher_load_balancer_data_volume_type_name,
            managed_rancher_tenant_max_cpu=managed_rancher_tenant_max_cpu,
            managed_rancher_tenant_max_ram=managed_rancher_tenant_max_ram,
            managed_rancher_tenant_max_disk=managed_rancher_tenant_max_disk,
            account_name_generation_policy=account_name_generation_policy,
        )

        merged_plugin_options_request.additional_properties = d
        return merged_plugin_options_request

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
