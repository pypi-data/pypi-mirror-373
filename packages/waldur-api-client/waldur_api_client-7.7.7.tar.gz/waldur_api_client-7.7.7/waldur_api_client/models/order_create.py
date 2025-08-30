import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.billing_unit import BillingUnit
from ..models.order_state import OrderState
from ..models.request_types import RequestTypes
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.order_create_limits import OrderCreateLimits


T = TypeVar("T", bound="OrderCreate")


@_attrs_define
class OrderCreate:
    """
    Attributes:
        offering (str):
        offering_name (str):
        offering_uuid (UUID):
        offering_description (str):
        offering_image (str):
        offering_thumbnail (str):
        offering_type (str):
        offering_shared (bool): Accessible to all customers.
        offering_billable (bool): Purchase and usage is invoiced.
        offering_plugin_options (Any): Public data used by specific plugin, such as storage mode for OpenStack.
        provider_name (str):
        provider_uuid (UUID):
        category_title (str):
        category_uuid (UUID):
        category_icon (str):
        plan_unit (Union[BillingUnit, None]):
        plan_name (Union[None, str]):
        plan_uuid (Union[None, UUID]):
        plan_description (Union[None, str]):
        uuid (UUID):
        created (datetime.datetime):
        modified (datetime.datetime):
        resource_uuid (Union[None, UUID]):
        resource_type (Union[None, str]):
        resource_name (str):
        cost (Union[None, str]):
        state (OrderState):
        output (str):
        marketplace_resource_uuid (UUID):
        error_message (str):
        completed_at (Union[None, datetime.datetime]):
        url (str):
        created_by (str):
        created_by_username (str): Required. 128 characters or fewer. Lowercase letters, numbers and @/./+/-/_
            characters
        created_by_full_name (str):
        consumer_reviewed_by (Union[None, str]):
        consumer_reviewed_at (Union[None, datetime.datetime]):
        consumer_reviewed_by_username (Union[None, str]): Required. 128 characters or fewer. Lowercase letters, numbers
            and @/./+/-/_ characters
        consumer_reviewed_by_full_name (Union[None, str]):
        project (str):
        project_uuid (UUID):
        project_name (str):
        project_description (str):
        customer_name (str):
        customer_uuid (UUID):
        plan (Union[Unset, str]):
        attributes (Union[Unset, Any]):
        limits (Union[Unset, OrderCreateLimits]):
        type_ (Union[Unset, RequestTypes]):  Default: RequestTypes.CREATE.
        callback_url (Union[None, Unset, str]):
    """

    offering: str
    offering_name: str
    offering_uuid: UUID
    offering_description: str
    offering_image: str
    offering_thumbnail: str
    offering_type: str
    offering_shared: bool
    offering_billable: bool
    offering_plugin_options: Any
    provider_name: str
    provider_uuid: UUID
    category_title: str
    category_uuid: UUID
    category_icon: str
    plan_unit: Union[BillingUnit, None]
    plan_name: Union[None, str]
    plan_uuid: Union[None, UUID]
    plan_description: Union[None, str]
    uuid: UUID
    created: datetime.datetime
    modified: datetime.datetime
    resource_uuid: Union[None, UUID]
    resource_type: Union[None, str]
    resource_name: str
    cost: Union[None, str]
    state: OrderState
    output: str
    marketplace_resource_uuid: UUID
    error_message: str
    completed_at: Union[None, datetime.datetime]
    url: str
    created_by: str
    created_by_username: str
    created_by_full_name: str
    consumer_reviewed_by: Union[None, str]
    consumer_reviewed_at: Union[None, datetime.datetime]
    consumer_reviewed_by_username: Union[None, str]
    consumer_reviewed_by_full_name: Union[None, str]
    project: str
    project_uuid: UUID
    project_name: str
    project_description: str
    customer_name: str
    customer_uuid: UUID
    plan: Union[Unset, str] = UNSET
    attributes: Union[Unset, Any] = UNSET
    limits: Union[Unset, "OrderCreateLimits"] = UNSET
    type_: Union[Unset, RequestTypes] = RequestTypes.CREATE
    callback_url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        offering = self.offering

        offering_name = self.offering_name

        offering_uuid = str(self.offering_uuid)

        offering_description = self.offering_description

        offering_image = self.offering_image

        offering_thumbnail = self.offering_thumbnail

        offering_type = self.offering_type

        offering_shared = self.offering_shared

        offering_billable = self.offering_billable

        offering_plugin_options = self.offering_plugin_options

        provider_name = self.provider_name

        provider_uuid = str(self.provider_uuid)

        category_title = self.category_title

        category_uuid = str(self.category_uuid)

        category_icon = self.category_icon

        plan_unit: Union[None, str]
        if isinstance(self.plan_unit, BillingUnit):
            plan_unit = self.plan_unit.value
        else:
            plan_unit = self.plan_unit

        plan_name: Union[None, str]
        plan_name = self.plan_name

        plan_uuid: Union[None, str]
        if isinstance(self.plan_uuid, UUID):
            plan_uuid = str(self.plan_uuid)
        else:
            plan_uuid = self.plan_uuid

        plan_description: Union[None, str]
        plan_description = self.plan_description

        uuid = str(self.uuid)

        created = self.created.isoformat()

        modified = self.modified.isoformat()

        resource_uuid: Union[None, str]
        if isinstance(self.resource_uuid, UUID):
            resource_uuid = str(self.resource_uuid)
        else:
            resource_uuid = self.resource_uuid

        resource_type: Union[None, str]
        resource_type = self.resource_type

        resource_name = self.resource_name

        cost: Union[None, str]
        cost = self.cost

        state = self.state.value

        output = self.output

        marketplace_resource_uuid = str(self.marketplace_resource_uuid)

        error_message = self.error_message

        completed_at: Union[None, str]
        if isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        url = self.url

        created_by = self.created_by

        created_by_username = self.created_by_username

        created_by_full_name = self.created_by_full_name

        consumer_reviewed_by: Union[None, str]
        consumer_reviewed_by = self.consumer_reviewed_by

        consumer_reviewed_at: Union[None, str]
        if isinstance(self.consumer_reviewed_at, datetime.datetime):
            consumer_reviewed_at = self.consumer_reviewed_at.isoformat()
        else:
            consumer_reviewed_at = self.consumer_reviewed_at

        consumer_reviewed_by_username: Union[None, str]
        consumer_reviewed_by_username = self.consumer_reviewed_by_username

        consumer_reviewed_by_full_name: Union[None, str]
        consumer_reviewed_by_full_name = self.consumer_reviewed_by_full_name

        project = self.project

        project_uuid = str(self.project_uuid)

        project_name = self.project_name

        project_description = self.project_description

        customer_name = self.customer_name

        customer_uuid = str(self.customer_uuid)

        plan = self.plan

        attributes = self.attributes

        limits: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.limits, Unset):
            limits = self.limits.to_dict()

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        callback_url: Union[None, Unset, str]
        if isinstance(self.callback_url, Unset):
            callback_url = UNSET
        else:
            callback_url = self.callback_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "offering": offering,
                "offering_name": offering_name,
                "offering_uuid": offering_uuid,
                "offering_description": offering_description,
                "offering_image": offering_image,
                "offering_thumbnail": offering_thumbnail,
                "offering_type": offering_type,
                "offering_shared": offering_shared,
                "offering_billable": offering_billable,
                "offering_plugin_options": offering_plugin_options,
                "provider_name": provider_name,
                "provider_uuid": provider_uuid,
                "category_title": category_title,
                "category_uuid": category_uuid,
                "category_icon": category_icon,
                "plan_unit": plan_unit,
                "plan_name": plan_name,
                "plan_uuid": plan_uuid,
                "plan_description": plan_description,
                "uuid": uuid,
                "created": created,
                "modified": modified,
                "resource_uuid": resource_uuid,
                "resource_type": resource_type,
                "resource_name": resource_name,
                "cost": cost,
                "state": state,
                "output": output,
                "marketplace_resource_uuid": marketplace_resource_uuid,
                "error_message": error_message,
                "completed_at": completed_at,
                "url": url,
                "created_by": created_by,
                "created_by_username": created_by_username,
                "created_by_full_name": created_by_full_name,
                "consumer_reviewed_by": consumer_reviewed_by,
                "consumer_reviewed_at": consumer_reviewed_at,
                "consumer_reviewed_by_username": consumer_reviewed_by_username,
                "consumer_reviewed_by_full_name": consumer_reviewed_by_full_name,
                "project": project,
                "project_uuid": project_uuid,
                "project_name": project_name,
                "project_description": project_description,
                "customer_name": customer_name,
                "customer_uuid": customer_uuid,
            }
        )
        if plan is not UNSET:
            field_dict["plan"] = plan
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if limits is not UNSET:
            field_dict["limits"] = limits
        if type_ is not UNSET:
            field_dict["type"] = type_
        if callback_url is not UNSET:
            field_dict["callback_url"] = callback_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.order_create_limits import OrderCreateLimits

        d = dict(src_dict)
        offering = d.pop("offering")

        offering_name = d.pop("offering_name")

        offering_uuid = UUID(d.pop("offering_uuid"))

        offering_description = d.pop("offering_description")

        offering_image = d.pop("offering_image")

        offering_thumbnail = d.pop("offering_thumbnail")

        offering_type = d.pop("offering_type")

        offering_shared = d.pop("offering_shared")

        offering_billable = d.pop("offering_billable")

        offering_plugin_options = d.pop("offering_plugin_options")

        provider_name = d.pop("provider_name")

        provider_uuid = UUID(d.pop("provider_uuid"))

        category_title = d.pop("category_title")

        category_uuid = UUID(d.pop("category_uuid"))

        category_icon = d.pop("category_icon")

        def _parse_plan_unit(data: object) -> Union[BillingUnit, None]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                plan_unit_type_1 = BillingUnit(data)

                return plan_unit_type_1
            except:  # noqa: E722
                pass
            return cast(Union[BillingUnit, None], data)

        plan_unit = _parse_plan_unit(d.pop("plan_unit"))

        def _parse_plan_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        plan_name = _parse_plan_name(d.pop("plan_name"))

        def _parse_plan_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                plan_uuid_type_0 = UUID(data)

                return plan_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        plan_uuid = _parse_plan_uuid(d.pop("plan_uuid"))

        def _parse_plan_description(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        plan_description = _parse_plan_description(d.pop("plan_description"))

        uuid = UUID(d.pop("uuid"))

        created = isoparse(d.pop("created"))

        modified = isoparse(d.pop("modified"))

        def _parse_resource_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                resource_uuid_type_0 = UUID(data)

                return resource_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        resource_uuid = _parse_resource_uuid(d.pop("resource_uuid"))

        def _parse_resource_type(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        resource_type = _parse_resource_type(d.pop("resource_type"))

        resource_name = d.pop("resource_name")

        def _parse_cost(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        cost = _parse_cost(d.pop("cost"))

        state = OrderState(d.pop("state"))

        output = d.pop("output")

        marketplace_resource_uuid = UUID(d.pop("marketplace_resource_uuid"))

        error_message = d.pop("error_message")

        def _parse_completed_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = isoparse(data)

                return completed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        completed_at = _parse_completed_at(d.pop("completed_at"))

        url = d.pop("url")

        created_by = d.pop("created_by")

        created_by_username = d.pop("created_by_username")

        created_by_full_name = d.pop("created_by_full_name")

        def _parse_consumer_reviewed_by(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        consumer_reviewed_by = _parse_consumer_reviewed_by(d.pop("consumer_reviewed_by"))

        def _parse_consumer_reviewed_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                consumer_reviewed_at_type_0 = isoparse(data)

                return consumer_reviewed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        consumer_reviewed_at = _parse_consumer_reviewed_at(d.pop("consumer_reviewed_at"))

        def _parse_consumer_reviewed_by_username(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        consumer_reviewed_by_username = _parse_consumer_reviewed_by_username(d.pop("consumer_reviewed_by_username"))

        def _parse_consumer_reviewed_by_full_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        consumer_reviewed_by_full_name = _parse_consumer_reviewed_by_full_name(d.pop("consumer_reviewed_by_full_name"))

        project = d.pop("project")

        project_uuid = UUID(d.pop("project_uuid"))

        project_name = d.pop("project_name")

        project_description = d.pop("project_description")

        customer_name = d.pop("customer_name")

        customer_uuid = UUID(d.pop("customer_uuid"))

        plan = d.pop("plan", UNSET)

        attributes = d.pop("attributes", UNSET)

        _limits = d.pop("limits", UNSET)
        limits: Union[Unset, OrderCreateLimits]
        if isinstance(_limits, Unset):
            limits = UNSET
        else:
            limits = OrderCreateLimits.from_dict(_limits)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, RequestTypes]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = RequestTypes(_type_)

        def _parse_callback_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        callback_url = _parse_callback_url(d.pop("callback_url", UNSET))

        order_create = cls(
            offering=offering,
            offering_name=offering_name,
            offering_uuid=offering_uuid,
            offering_description=offering_description,
            offering_image=offering_image,
            offering_thumbnail=offering_thumbnail,
            offering_type=offering_type,
            offering_shared=offering_shared,
            offering_billable=offering_billable,
            offering_plugin_options=offering_plugin_options,
            provider_name=provider_name,
            provider_uuid=provider_uuid,
            category_title=category_title,
            category_uuid=category_uuid,
            category_icon=category_icon,
            plan_unit=plan_unit,
            plan_name=plan_name,
            plan_uuid=plan_uuid,
            plan_description=plan_description,
            uuid=uuid,
            created=created,
            modified=modified,
            resource_uuid=resource_uuid,
            resource_type=resource_type,
            resource_name=resource_name,
            cost=cost,
            state=state,
            output=output,
            marketplace_resource_uuid=marketplace_resource_uuid,
            error_message=error_message,
            completed_at=completed_at,
            url=url,
            created_by=created_by,
            created_by_username=created_by_username,
            created_by_full_name=created_by_full_name,
            consumer_reviewed_by=consumer_reviewed_by,
            consumer_reviewed_at=consumer_reviewed_at,
            consumer_reviewed_by_username=consumer_reviewed_by_username,
            consumer_reviewed_by_full_name=consumer_reviewed_by_full_name,
            project=project,
            project_uuid=project_uuid,
            project_name=project_name,
            project_description=project_description,
            customer_name=customer_name,
            customer_uuid=customer_uuid,
            plan=plan,
            attributes=attributes,
            limits=limits,
            type_=type_,
            callback_url=callback_url,
        )

        order_create.additional_properties = d
        return order_create

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
