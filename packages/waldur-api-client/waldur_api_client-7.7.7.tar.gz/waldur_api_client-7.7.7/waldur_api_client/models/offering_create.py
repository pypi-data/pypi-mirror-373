import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.blank_enum import BlankEnum
from ..models.core_states import CoreStates
from ..models.country_enum import CountryEnum
from ..models.offering_state import OfferingState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.base_provider_plan import BaseProviderPlan
    from ..models.merged_plugin_options import MergedPluginOptions
    from ..models.merged_secret_options import MergedSecretOptions
    from ..models.nested_endpoint import NestedEndpoint
    from ..models.nested_offering_file import NestedOfferingFile
    from ..models.nested_role import NestedRole
    from ..models.nested_screenshot import NestedScreenshot
    from ..models.offering_component import OfferingComponent
    from ..models.offering_create_service_attributes import OfferingCreateServiceAttributes
    from ..models.offering_options import OfferingOptions
    from ..models.organization_group import OrganizationGroup
    from ..models.quota import Quota


T = TypeVar("T", bound="OfferingCreate")


@_attrs_define
class OfferingCreate:
    """
    Attributes:
        url (str):
        uuid (UUID):
        created (datetime.datetime):
        name (str):
        slug (str):
        endpoints (list['NestedEndpoint']):
        roles (list['NestedRole']):
        customer_uuid (Union[None, UUID]):
        customer_name (Union[None, str]):
        project (Union[None, str]):
        project_uuid (Union[None, UUID]):
        project_name (Union[None, str]):
        category (str):
        category_uuid (UUID):
        category_title (str):
        plugin_options (MergedPluginOptions):
        secret_options (MergedSecretOptions):
        service_attributes (OfferingCreateServiceAttributes):
        state (OfferingState):
        order_count (int):
        screenshots (list['NestedScreenshot']):
        type_ (str):
        scope (str):
        scope_uuid (Union[None, UUID]):
        scope_name (Union[None, UUID]):
        scope_state (Union[CoreStates, None]):
        scope_error_message (Union[None, str]):
        files (list['NestedOfferingFile']):
        quotas (list['Quota']):
        paused_reason (str):
        citation_count (int): Number of citations of a DOI
        organization_groups (list['OrganizationGroup']):
        total_customers (Union[None, int]):
        total_cost (Union[None, int]):
        total_cost_estimated (Union[None, int]):
        parent_description (Union[None, str]):
        parent_uuid (Union[None, UUID]):
        parent_name (Union[None, str]):
        has_compliance_requirements (bool):
        description (Union[Unset, str]):
        full_description (Union[Unset, str]):
        privacy_policy_link (Union[Unset, str]):
        access_url (Union[Unset, str]): Publicly accessible offering access URL
        customer (Union[None, Unset, str]):
        attributes (Union[Unset, Any]):
        options (Union[Unset, OfferingOptions]):
        resource_options (Union[Unset, OfferingOptions]):
        components (Union[Unset, list['OfferingComponent']]):
        vendor_details (Union[Unset, str]):
        getting_started (Union[Unset, str]):
        integration_guide (Union[Unset, str]):
        thumbnail (Union[None, Unset, str]):
        plans (Union[Unset, list['BaseProviderPlan']]):
        shared (Union[Unset, bool]): Accessible to all customers.
        billable (Union[Unset, bool]): Purchase and usage is invoiced.
        datacite_doi (Union[Unset, str]):
        latitude (Union[None, Unset, float]):
        longitude (Union[None, Unset, float]):
        country (Union[BlankEnum, CountryEnum, Unset]):
        backend_id (Union[Unset, str]):
        image (Union[None, Unset, str]):
        backend_metadata (Union[Unset, Any]):
    """

    url: str
    uuid: UUID
    created: datetime.datetime
    name: str
    slug: str
    endpoints: list["NestedEndpoint"]
    roles: list["NestedRole"]
    customer_uuid: Union[None, UUID]
    customer_name: Union[None, str]
    project: Union[None, str]
    project_uuid: Union[None, UUID]
    project_name: Union[None, str]
    category: str
    category_uuid: UUID
    category_title: str
    plugin_options: "MergedPluginOptions"
    secret_options: "MergedSecretOptions"
    service_attributes: "OfferingCreateServiceAttributes"
    state: OfferingState
    order_count: int
    screenshots: list["NestedScreenshot"]
    type_: str
    scope: str
    scope_uuid: Union[None, UUID]
    scope_name: Union[None, UUID]
    scope_state: Union[CoreStates, None]
    scope_error_message: Union[None, str]
    files: list["NestedOfferingFile"]
    quotas: list["Quota"]
    paused_reason: str
    citation_count: int
    organization_groups: list["OrganizationGroup"]
    total_customers: Union[None, int]
    total_cost: Union[None, int]
    total_cost_estimated: Union[None, int]
    parent_description: Union[None, str]
    parent_uuid: Union[None, UUID]
    parent_name: Union[None, str]
    has_compliance_requirements: bool
    description: Union[Unset, str] = UNSET
    full_description: Union[Unset, str] = UNSET
    privacy_policy_link: Union[Unset, str] = UNSET
    access_url: Union[Unset, str] = UNSET
    customer: Union[None, Unset, str] = UNSET
    attributes: Union[Unset, Any] = UNSET
    options: Union[Unset, "OfferingOptions"] = UNSET
    resource_options: Union[Unset, "OfferingOptions"] = UNSET
    components: Union[Unset, list["OfferingComponent"]] = UNSET
    vendor_details: Union[Unset, str] = UNSET
    getting_started: Union[Unset, str] = UNSET
    integration_guide: Union[Unset, str] = UNSET
    thumbnail: Union[None, Unset, str] = UNSET
    plans: Union[Unset, list["BaseProviderPlan"]] = UNSET
    shared: Union[Unset, bool] = UNSET
    billable: Union[Unset, bool] = UNSET
    datacite_doi: Union[Unset, str] = UNSET
    latitude: Union[None, Unset, float] = UNSET
    longitude: Union[None, Unset, float] = UNSET
    country: Union[BlankEnum, CountryEnum, Unset] = UNSET
    backend_id: Union[Unset, str] = UNSET
    image: Union[None, Unset, str] = UNSET
    backend_metadata: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid = str(self.uuid)

        created = self.created.isoformat()

        name = self.name

        slug = self.slug

        endpoints = []
        for endpoints_item_data in self.endpoints:
            endpoints_item = endpoints_item_data.to_dict()
            endpoints.append(endpoints_item)

        roles = []
        for roles_item_data in self.roles:
            roles_item = roles_item_data.to_dict()
            roles.append(roles_item)

        customer_uuid: Union[None, str]
        if isinstance(self.customer_uuid, UUID):
            customer_uuid = str(self.customer_uuid)
        else:
            customer_uuid = self.customer_uuid

        customer_name: Union[None, str]
        customer_name = self.customer_name

        project: Union[None, str]
        project = self.project

        project_uuid: Union[None, str]
        if isinstance(self.project_uuid, UUID):
            project_uuid = str(self.project_uuid)
        else:
            project_uuid = self.project_uuid

        project_name: Union[None, str]
        project_name = self.project_name

        category = self.category

        category_uuid = str(self.category_uuid)

        category_title = self.category_title

        plugin_options = self.plugin_options.to_dict()

        secret_options = self.secret_options.to_dict()

        service_attributes = self.service_attributes.to_dict()

        state = self.state.value

        order_count = self.order_count

        screenshots = []
        for screenshots_item_data in self.screenshots:
            screenshots_item = screenshots_item_data.to_dict()
            screenshots.append(screenshots_item)

        type_ = self.type_

        scope = self.scope

        scope_uuid: Union[None, str]
        if isinstance(self.scope_uuid, UUID):
            scope_uuid = str(self.scope_uuid)
        else:
            scope_uuid = self.scope_uuid

        scope_name: Union[None, str]
        if isinstance(self.scope_name, UUID):
            scope_name = str(self.scope_name)
        else:
            scope_name = self.scope_name

        scope_state: Union[None, str]
        if isinstance(self.scope_state, CoreStates):
            scope_state = self.scope_state.value
        else:
            scope_state = self.scope_state

        scope_error_message: Union[None, str]
        scope_error_message = self.scope_error_message

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        quotas = []
        for quotas_item_data in self.quotas:
            quotas_item = quotas_item_data.to_dict()
            quotas.append(quotas_item)

        paused_reason = self.paused_reason

        citation_count = self.citation_count

        organization_groups = []
        for organization_groups_item_data in self.organization_groups:
            organization_groups_item = organization_groups_item_data.to_dict()
            organization_groups.append(organization_groups_item)

        total_customers: Union[None, int]
        total_customers = self.total_customers

        total_cost: Union[None, int]
        total_cost = self.total_cost

        total_cost_estimated: Union[None, int]
        total_cost_estimated = self.total_cost_estimated

        parent_description: Union[None, str]
        parent_description = self.parent_description

        parent_uuid: Union[None, str]
        if isinstance(self.parent_uuid, UUID):
            parent_uuid = str(self.parent_uuid)
        else:
            parent_uuid = self.parent_uuid

        parent_name: Union[None, str]
        parent_name = self.parent_name

        has_compliance_requirements = self.has_compliance_requirements

        description = self.description

        full_description = self.full_description

        privacy_policy_link = self.privacy_policy_link

        access_url = self.access_url

        customer: Union[None, Unset, str]
        if isinstance(self.customer, Unset):
            customer = UNSET
        else:
            customer = self.customer

        attributes = self.attributes

        options: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        resource_options: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.resource_options, Unset):
            resource_options = self.resource_options.to_dict()

        components: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.components, Unset):
            components = []
            for components_item_data in self.components:
                components_item = components_item_data.to_dict()
                components.append(components_item)

        vendor_details = self.vendor_details

        getting_started = self.getting_started

        integration_guide = self.integration_guide

        thumbnail: Union[None, Unset, str]
        if isinstance(self.thumbnail, Unset):
            thumbnail = UNSET
        else:
            thumbnail = self.thumbnail

        plans: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.plans, Unset):
            plans = []
            for plans_item_data in self.plans:
                plans_item = plans_item_data.to_dict()
                plans.append(plans_item)

        shared = self.shared

        billable = self.billable

        datacite_doi = self.datacite_doi

        latitude: Union[None, Unset, float]
        if isinstance(self.latitude, Unset):
            latitude = UNSET
        else:
            latitude = self.latitude

        longitude: Union[None, Unset, float]
        if isinstance(self.longitude, Unset):
            longitude = UNSET
        else:
            longitude = self.longitude

        country: Union[Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        elif isinstance(self.country, CountryEnum):
            country = self.country.value
        else:
            country = self.country.value

        backend_id = self.backend_id

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        backend_metadata = self.backend_metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "created": created,
                "name": name,
                "slug": slug,
                "endpoints": endpoints,
                "roles": roles,
                "customer_uuid": customer_uuid,
                "customer_name": customer_name,
                "project": project,
                "project_uuid": project_uuid,
                "project_name": project_name,
                "category": category,
                "category_uuid": category_uuid,
                "category_title": category_title,
                "plugin_options": plugin_options,
                "secret_options": secret_options,
                "service_attributes": service_attributes,
                "state": state,
                "order_count": order_count,
                "screenshots": screenshots,
                "type": type_,
                "scope": scope,
                "scope_uuid": scope_uuid,
                "scope_name": scope_name,
                "scope_state": scope_state,
                "scope_error_message": scope_error_message,
                "files": files,
                "quotas": quotas,
                "paused_reason": paused_reason,
                "citation_count": citation_count,
                "organization_groups": organization_groups,
                "total_customers": total_customers,
                "total_cost": total_cost,
                "total_cost_estimated": total_cost_estimated,
                "parent_description": parent_description,
                "parent_uuid": parent_uuid,
                "parent_name": parent_name,
                "has_compliance_requirements": has_compliance_requirements,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if full_description is not UNSET:
            field_dict["full_description"] = full_description
        if privacy_policy_link is not UNSET:
            field_dict["privacy_policy_link"] = privacy_policy_link
        if access_url is not UNSET:
            field_dict["access_url"] = access_url
        if customer is not UNSET:
            field_dict["customer"] = customer
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if options is not UNSET:
            field_dict["options"] = options
        if resource_options is not UNSET:
            field_dict["resource_options"] = resource_options
        if components is not UNSET:
            field_dict["components"] = components
        if vendor_details is not UNSET:
            field_dict["vendor_details"] = vendor_details
        if getting_started is not UNSET:
            field_dict["getting_started"] = getting_started
        if integration_guide is not UNSET:
            field_dict["integration_guide"] = integration_guide
        if thumbnail is not UNSET:
            field_dict["thumbnail"] = thumbnail
        if plans is not UNSET:
            field_dict["plans"] = plans
        if shared is not UNSET:
            field_dict["shared"] = shared
        if billable is not UNSET:
            field_dict["billable"] = billable
        if datacite_doi is not UNSET:
            field_dict["datacite_doi"] = datacite_doi
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if country is not UNSET:
            field_dict["country"] = country
        if backend_id is not UNSET:
            field_dict["backend_id"] = backend_id
        if image is not UNSET:
            field_dict["image"] = image
        if backend_metadata is not UNSET:
            field_dict["backend_metadata"] = backend_metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.base_provider_plan import BaseProviderPlan
        from ..models.merged_plugin_options import MergedPluginOptions
        from ..models.merged_secret_options import MergedSecretOptions
        from ..models.nested_endpoint import NestedEndpoint
        from ..models.nested_offering_file import NestedOfferingFile
        from ..models.nested_role import NestedRole
        from ..models.nested_screenshot import NestedScreenshot
        from ..models.offering_component import OfferingComponent
        from ..models.offering_create_service_attributes import OfferingCreateServiceAttributes
        from ..models.offering_options import OfferingOptions
        from ..models.organization_group import OrganizationGroup
        from ..models.quota import Quota

        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        created = isoparse(d.pop("created"))

        name = d.pop("name")

        slug = d.pop("slug")

        endpoints = []
        _endpoints = d.pop("endpoints")
        for endpoints_item_data in _endpoints:
            endpoints_item = NestedEndpoint.from_dict(endpoints_item_data)

            endpoints.append(endpoints_item)

        roles = []
        _roles = d.pop("roles")
        for roles_item_data in _roles:
            roles_item = NestedRole.from_dict(roles_item_data)

            roles.append(roles_item)

        def _parse_customer_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                customer_uuid_type_0 = UUID(data)

                return customer_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        customer_uuid = _parse_customer_uuid(d.pop("customer_uuid"))

        def _parse_customer_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        customer_name = _parse_customer_name(d.pop("customer_name"))

        def _parse_project(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        project = _parse_project(d.pop("project"))

        def _parse_project_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                project_uuid_type_0 = UUID(data)

                return project_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        project_uuid = _parse_project_uuid(d.pop("project_uuid"))

        def _parse_project_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        project_name = _parse_project_name(d.pop("project_name"))

        category = d.pop("category")

        category_uuid = UUID(d.pop("category_uuid"))

        category_title = d.pop("category_title")

        plugin_options = MergedPluginOptions.from_dict(d.pop("plugin_options"))

        secret_options = MergedSecretOptions.from_dict(d.pop("secret_options"))

        service_attributes = OfferingCreateServiceAttributes.from_dict(d.pop("service_attributes"))

        state = OfferingState(d.pop("state"))

        order_count = d.pop("order_count")

        screenshots = []
        _screenshots = d.pop("screenshots")
        for screenshots_item_data in _screenshots:
            screenshots_item = NestedScreenshot.from_dict(screenshots_item_data)

            screenshots.append(screenshots_item)

        type_ = d.pop("type")

        scope = d.pop("scope")

        def _parse_scope_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                scope_uuid_type_0 = UUID(data)

                return scope_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        scope_uuid = _parse_scope_uuid(d.pop("scope_uuid"))

        def _parse_scope_name(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                scope_name_type_0 = UUID(data)

                return scope_name_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        scope_name = _parse_scope_name(d.pop("scope_name"))

        def _parse_scope_state(data: object) -> Union[CoreStates, None]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                scope_state_type_1 = CoreStates(data)

                return scope_state_type_1
            except:  # noqa: E722
                pass
            return cast(Union[CoreStates, None], data)

        scope_state = _parse_scope_state(d.pop("scope_state"))

        def _parse_scope_error_message(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        scope_error_message = _parse_scope_error_message(d.pop("scope_error_message"))

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = NestedOfferingFile.from_dict(files_item_data)

            files.append(files_item)

        quotas = []
        _quotas = d.pop("quotas")
        for quotas_item_data in _quotas:
            quotas_item = Quota.from_dict(quotas_item_data)

            quotas.append(quotas_item)

        paused_reason = d.pop("paused_reason")

        citation_count = d.pop("citation_count")

        organization_groups = []
        _organization_groups = d.pop("organization_groups")
        for organization_groups_item_data in _organization_groups:
            organization_groups_item = OrganizationGroup.from_dict(organization_groups_item_data)

            organization_groups.append(organization_groups_item)

        def _parse_total_customers(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        total_customers = _parse_total_customers(d.pop("total_customers"))

        def _parse_total_cost(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        total_cost = _parse_total_cost(d.pop("total_cost"))

        def _parse_total_cost_estimated(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        total_cost_estimated = _parse_total_cost_estimated(d.pop("total_cost_estimated"))

        def _parse_parent_description(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        parent_description = _parse_parent_description(d.pop("parent_description"))

        def _parse_parent_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                parent_uuid_type_0 = UUID(data)

                return parent_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        parent_uuid = _parse_parent_uuid(d.pop("parent_uuid"))

        def _parse_parent_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        parent_name = _parse_parent_name(d.pop("parent_name"))

        has_compliance_requirements = d.pop("has_compliance_requirements")

        description = d.pop("description", UNSET)

        full_description = d.pop("full_description", UNSET)

        privacy_policy_link = d.pop("privacy_policy_link", UNSET)

        access_url = d.pop("access_url", UNSET)

        def _parse_customer(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        customer = _parse_customer(d.pop("customer", UNSET))

        attributes = d.pop("attributes", UNSET)

        _options = d.pop("options", UNSET)
        options: Union[Unset, OfferingOptions]
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = OfferingOptions.from_dict(_options)

        _resource_options = d.pop("resource_options", UNSET)
        resource_options: Union[Unset, OfferingOptions]
        if isinstance(_resource_options, Unset):
            resource_options = UNSET
        else:
            resource_options = OfferingOptions.from_dict(_resource_options)

        components = []
        _components = d.pop("components", UNSET)
        for components_item_data in _components or []:
            components_item = OfferingComponent.from_dict(components_item_data)

            components.append(components_item)

        vendor_details = d.pop("vendor_details", UNSET)

        getting_started = d.pop("getting_started", UNSET)

        integration_guide = d.pop("integration_guide", UNSET)

        def _parse_thumbnail(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        thumbnail = _parse_thumbnail(d.pop("thumbnail", UNSET))

        plans = []
        _plans = d.pop("plans", UNSET)
        for plans_item_data in _plans or []:
            plans_item = BaseProviderPlan.from_dict(plans_item_data)

            plans.append(plans_item)

        shared = d.pop("shared", UNSET)

        billable = d.pop("billable", UNSET)

        datacite_doi = d.pop("datacite_doi", UNSET)

        def _parse_latitude(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        latitude = _parse_latitude(d.pop("latitude", UNSET))

        def _parse_longitude(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        longitude = _parse_longitude(d.pop("longitude", UNSET))

        def _parse_country(data: object) -> Union[BlankEnum, CountryEnum, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                country_type_0 = CountryEnum(data)

                return country_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            country_type_1 = BlankEnum(data)

            return country_type_1

        country = _parse_country(d.pop("country", UNSET))

        backend_id = d.pop("backend_id", UNSET)

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        backend_metadata = d.pop("backend_metadata", UNSET)

        offering_create = cls(
            url=url,
            uuid=uuid,
            created=created,
            name=name,
            slug=slug,
            endpoints=endpoints,
            roles=roles,
            customer_uuid=customer_uuid,
            customer_name=customer_name,
            project=project,
            project_uuid=project_uuid,
            project_name=project_name,
            category=category,
            category_uuid=category_uuid,
            category_title=category_title,
            plugin_options=plugin_options,
            secret_options=secret_options,
            service_attributes=service_attributes,
            state=state,
            order_count=order_count,
            screenshots=screenshots,
            type_=type_,
            scope=scope,
            scope_uuid=scope_uuid,
            scope_name=scope_name,
            scope_state=scope_state,
            scope_error_message=scope_error_message,
            files=files,
            quotas=quotas,
            paused_reason=paused_reason,
            citation_count=citation_count,
            organization_groups=organization_groups,
            total_customers=total_customers,
            total_cost=total_cost,
            total_cost_estimated=total_cost_estimated,
            parent_description=parent_description,
            parent_uuid=parent_uuid,
            parent_name=parent_name,
            has_compliance_requirements=has_compliance_requirements,
            description=description,
            full_description=full_description,
            privacy_policy_link=privacy_policy_link,
            access_url=access_url,
            customer=customer,
            attributes=attributes,
            options=options,
            resource_options=resource_options,
            components=components,
            vendor_details=vendor_details,
            getting_started=getting_started,
            integration_guide=integration_guide,
            thumbnail=thumbnail,
            plans=plans,
            shared=shared,
            billable=billable,
            datacite_doi=datacite_doi,
            latitude=latitude,
            longitude=longitude,
            country=country,
            backend_id=backend_id,
            image=image,
            backend_metadata=backend_metadata,
        )

        offering_create.additional_properties = d
        return offering_create

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
