import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.marketplace_provider_offerings_component_stats_list_o_item import (
    MarketplaceProviderOfferingsComponentStatsListOItem,
)
from ...models.marketplace_provider_offerings_component_stats_list_state_item import (
    MarketplaceProviderOfferingsComponentStatsListStateItem,
)
from ...models.offering_component_stat import OfferingComponentStat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    uuid: UUID,
    *,
    accessible_via_calls: Union[Unset, bool] = UNSET,
    allowed_customer_uuid: Union[Unset, UUID] = UNSET,
    attributes: Union[Unset, str] = UNSET,
    billable: Union[Unset, bool] = UNSET,
    category_group_uuid: Union[Unset, UUID] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    description: Union[Unset, str] = UNSET,
    end: Union[Unset, str] = UNSET,
    keyword: Union[Unset, str] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_uuid: Union[Unset, UUID] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    resource_customer_uuid: Union[Unset, UUID] = UNSET,
    resource_project_uuid: Union[Unset, UUID] = UNSET,
    scope_uuid: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
    start: Union[Unset, str] = UNSET,
    state: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    uuid_list: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["accessible_via_calls"] = accessible_via_calls

    json_allowed_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(allowed_customer_uuid, Unset):
        json_allowed_customer_uuid = str(allowed_customer_uuid)
    params["allowed_customer_uuid"] = json_allowed_customer_uuid

    params["attributes"] = attributes

    params["billable"] = billable

    json_category_group_uuid: Union[Unset, str] = UNSET
    if not isinstance(category_group_uuid, Unset):
        json_category_group_uuid = str(category_group_uuid)
    params["category_group_uuid"] = json_category_group_uuid

    json_category_uuid: Union[Unset, str] = UNSET
    if not isinstance(category_uuid, Unset):
        json_category_uuid = str(category_uuid)
    params["category_uuid"] = json_category_uuid

    json_created: Union[Unset, str] = UNSET
    if not isinstance(created, Unset):
        json_created = created.isoformat()
    params["created"] = json_created

    params["customer"] = customer

    json_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(customer_uuid, Unset):
        json_customer_uuid = str(customer_uuid)
    params["customer_uuid"] = json_customer_uuid

    params["description"] = description

    params["end"] = end

    params["keyword"] = keyword

    json_modified: Union[Unset, str] = UNSET
    if not isinstance(modified, Unset):
        json_modified = modified.isoformat()
    params["modified"] = json_modified

    params["name"] = name

    params["name_exact"] = name_exact

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    json_organization_group_uuid: Union[Unset, list[str]] = UNSET
    if not isinstance(organization_group_uuid, Unset):
        json_organization_group_uuid = []
        for organization_group_uuid_item_data in organization_group_uuid:
            organization_group_uuid_item = str(organization_group_uuid_item_data)
            json_organization_group_uuid.append(organization_group_uuid_item)

    params["organization_group_uuid"] = json_organization_group_uuid

    params["page"] = page

    params["page_size"] = page_size

    json_parent_uuid: Union[Unset, str] = UNSET
    if not isinstance(parent_uuid, Unset):
        json_parent_uuid = str(parent_uuid)
    params["parent_uuid"] = json_parent_uuid

    json_project_uuid: Union[Unset, str] = UNSET
    if not isinstance(project_uuid, Unset):
        json_project_uuid = str(project_uuid)
    params["project_uuid"] = json_project_uuid

    json_resource_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(resource_customer_uuid, Unset):
        json_resource_customer_uuid = str(resource_customer_uuid)
    params["resource_customer_uuid"] = json_resource_customer_uuid

    json_resource_project_uuid: Union[Unset, str] = UNSET
    if not isinstance(resource_project_uuid, Unset):
        json_resource_project_uuid = str(resource_project_uuid)
    params["resource_project_uuid"] = json_resource_project_uuid

    params["scope_uuid"] = scope_uuid

    json_service_manager_uuid: Union[Unset, str] = UNSET
    if not isinstance(service_manager_uuid, Unset):
        json_service_manager_uuid = str(service_manager_uuid)
    params["service_manager_uuid"] = json_service_manager_uuid

    params["shared"] = shared

    params["start"] = start

    json_state: Union[Unset, list[str]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    json_type_: Union[Unset, list[str]] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_

    params["type"] = json_type_

    params["uuid_list"] = uuid_list

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/marketplace-provider-offerings/{uuid}/component_stats/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["OfferingComponentStat"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = OfferingComponentStat.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["OfferingComponentStat"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    accessible_via_calls: Union[Unset, bool] = UNSET,
    allowed_customer_uuid: Union[Unset, UUID] = UNSET,
    attributes: Union[Unset, str] = UNSET,
    billable: Union[Unset, bool] = UNSET,
    category_group_uuid: Union[Unset, UUID] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    description: Union[Unset, str] = UNSET,
    end: Union[Unset, str] = UNSET,
    keyword: Union[Unset, str] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_uuid: Union[Unset, UUID] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    resource_customer_uuid: Union[Unset, UUID] = UNSET,
    resource_project_uuid: Union[Unset, UUID] = UNSET,
    scope_uuid: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
    start: Union[Unset, str] = UNSET,
    state: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    uuid_list: Union[Unset, str] = UNSET,
) -> Response[list["OfferingComponentStat"]]:
    """Get statistics for offering components.

    Args:
        uuid (UUID):
        accessible_via_calls (Union[Unset, bool]):
        allowed_customer_uuid (Union[Unset, UUID]):
        attributes (Union[Unset, str]):
        billable (Union[Unset, bool]):
        category_group_uuid (Union[Unset, UUID]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        description (Union[Unset, str]):
        end (Union[Unset, str]):
        keyword (Union[Unset, str]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_uuid (Union[Unset, UUID]):
        project_uuid (Union[Unset, UUID]):
        resource_customer_uuid (Union[Unset, UUID]):
        resource_project_uuid (Union[Unset, UUID]):
        scope_uuid (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):
        start (Union[Unset, str]):
        state (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]]):
        type_ (Union[Unset, list[str]]):
        uuid_list (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['OfferingComponentStat']]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        accessible_via_calls=accessible_via_calls,
        allowed_customer_uuid=allowed_customer_uuid,
        attributes=attributes,
        billable=billable,
        category_group_uuid=category_group_uuid,
        category_uuid=category_uuid,
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        description=description,
        end=end,
        keyword=keyword,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        organization_group_uuid=organization_group_uuid,
        page=page,
        page_size=page_size,
        parent_uuid=parent_uuid,
        project_uuid=project_uuid,
        resource_customer_uuid=resource_customer_uuid,
        resource_project_uuid=resource_project_uuid,
        scope_uuid=scope_uuid,
        service_manager_uuid=service_manager_uuid,
        shared=shared,
        start=start,
        state=state,
        type_=type_,
        uuid_list=uuid_list,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    accessible_via_calls: Union[Unset, bool] = UNSET,
    allowed_customer_uuid: Union[Unset, UUID] = UNSET,
    attributes: Union[Unset, str] = UNSET,
    billable: Union[Unset, bool] = UNSET,
    category_group_uuid: Union[Unset, UUID] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    description: Union[Unset, str] = UNSET,
    end: Union[Unset, str] = UNSET,
    keyword: Union[Unset, str] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_uuid: Union[Unset, UUID] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    resource_customer_uuid: Union[Unset, UUID] = UNSET,
    resource_project_uuid: Union[Unset, UUID] = UNSET,
    scope_uuid: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
    start: Union[Unset, str] = UNSET,
    state: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    uuid_list: Union[Unset, str] = UNSET,
) -> list["OfferingComponentStat"]:
    """Get statistics for offering components.

    Args:
        uuid (UUID):
        accessible_via_calls (Union[Unset, bool]):
        allowed_customer_uuid (Union[Unset, UUID]):
        attributes (Union[Unset, str]):
        billable (Union[Unset, bool]):
        category_group_uuid (Union[Unset, UUID]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        description (Union[Unset, str]):
        end (Union[Unset, str]):
        keyword (Union[Unset, str]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_uuid (Union[Unset, UUID]):
        project_uuid (Union[Unset, UUID]):
        resource_customer_uuid (Union[Unset, UUID]):
        resource_project_uuid (Union[Unset, UUID]):
        scope_uuid (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):
        start (Union[Unset, str]):
        state (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]]):
        type_ (Union[Unset, list[str]]):
        uuid_list (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['OfferingComponentStat']
    """

    return sync_detailed(
        uuid=uuid,
        client=client,
        accessible_via_calls=accessible_via_calls,
        allowed_customer_uuid=allowed_customer_uuid,
        attributes=attributes,
        billable=billable,
        category_group_uuid=category_group_uuid,
        category_uuid=category_uuid,
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        description=description,
        end=end,
        keyword=keyword,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        organization_group_uuid=organization_group_uuid,
        page=page,
        page_size=page_size,
        parent_uuid=parent_uuid,
        project_uuid=project_uuid,
        resource_customer_uuid=resource_customer_uuid,
        resource_project_uuid=resource_project_uuid,
        scope_uuid=scope_uuid,
        service_manager_uuid=service_manager_uuid,
        shared=shared,
        start=start,
        state=state,
        type_=type_,
        uuid_list=uuid_list,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    accessible_via_calls: Union[Unset, bool] = UNSET,
    allowed_customer_uuid: Union[Unset, UUID] = UNSET,
    attributes: Union[Unset, str] = UNSET,
    billable: Union[Unset, bool] = UNSET,
    category_group_uuid: Union[Unset, UUID] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    description: Union[Unset, str] = UNSET,
    end: Union[Unset, str] = UNSET,
    keyword: Union[Unset, str] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_uuid: Union[Unset, UUID] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    resource_customer_uuid: Union[Unset, UUID] = UNSET,
    resource_project_uuid: Union[Unset, UUID] = UNSET,
    scope_uuid: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
    start: Union[Unset, str] = UNSET,
    state: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    uuid_list: Union[Unset, str] = UNSET,
) -> Response[list["OfferingComponentStat"]]:
    """Get statistics for offering components.

    Args:
        uuid (UUID):
        accessible_via_calls (Union[Unset, bool]):
        allowed_customer_uuid (Union[Unset, UUID]):
        attributes (Union[Unset, str]):
        billable (Union[Unset, bool]):
        category_group_uuid (Union[Unset, UUID]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        description (Union[Unset, str]):
        end (Union[Unset, str]):
        keyword (Union[Unset, str]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_uuid (Union[Unset, UUID]):
        project_uuid (Union[Unset, UUID]):
        resource_customer_uuid (Union[Unset, UUID]):
        resource_project_uuid (Union[Unset, UUID]):
        scope_uuid (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):
        start (Union[Unset, str]):
        state (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]]):
        type_ (Union[Unset, list[str]]):
        uuid_list (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['OfferingComponentStat']]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        accessible_via_calls=accessible_via_calls,
        allowed_customer_uuid=allowed_customer_uuid,
        attributes=attributes,
        billable=billable,
        category_group_uuid=category_group_uuid,
        category_uuid=category_uuid,
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        description=description,
        end=end,
        keyword=keyword,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        organization_group_uuid=organization_group_uuid,
        page=page,
        page_size=page_size,
        parent_uuid=parent_uuid,
        project_uuid=project_uuid,
        resource_customer_uuid=resource_customer_uuid,
        resource_project_uuid=resource_project_uuid,
        scope_uuid=scope_uuid,
        service_manager_uuid=service_manager_uuid,
        shared=shared,
        start=start,
        state=state,
        type_=type_,
        uuid_list=uuid_list,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    accessible_via_calls: Union[Unset, bool] = UNSET,
    allowed_customer_uuid: Union[Unset, UUID] = UNSET,
    attributes: Union[Unset, str] = UNSET,
    billable: Union[Unset, bool] = UNSET,
    category_group_uuid: Union[Unset, UUID] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    description: Union[Unset, str] = UNSET,
    end: Union[Unset, str] = UNSET,
    keyword: Union[Unset, str] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_uuid: Union[Unset, UUID] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    resource_customer_uuid: Union[Unset, UUID] = UNSET,
    resource_project_uuid: Union[Unset, UUID] = UNSET,
    scope_uuid: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
    start: Union[Unset, str] = UNSET,
    state: Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]] = UNSET,
    type_: Union[Unset, list[str]] = UNSET,
    uuid_list: Union[Unset, str] = UNSET,
) -> list["OfferingComponentStat"]:
    """Get statistics for offering components.

    Args:
        uuid (UUID):
        accessible_via_calls (Union[Unset, bool]):
        allowed_customer_uuid (Union[Unset, UUID]):
        attributes (Union[Unset, str]):
        billable (Union[Unset, bool]):
        category_group_uuid (Union[Unset, UUID]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        description (Union[Unset, str]):
        end (Union[Unset, str]):
        keyword (Union[Unset, str]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListOItem]]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_uuid (Union[Unset, UUID]):
        project_uuid (Union[Unset, UUID]):
        resource_customer_uuid (Union[Unset, UUID]):
        resource_project_uuid (Union[Unset, UUID]):
        scope_uuid (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):
        start (Union[Unset, str]):
        state (Union[Unset, list[MarketplaceProviderOfferingsComponentStatsListStateItem]]):
        type_ (Union[Unset, list[str]]):
        uuid_list (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['OfferingComponentStat']
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            accessible_via_calls=accessible_via_calls,
            allowed_customer_uuid=allowed_customer_uuid,
            attributes=attributes,
            billable=billable,
            category_group_uuid=category_group_uuid,
            category_uuid=category_uuid,
            created=created,
            customer=customer,
            customer_uuid=customer_uuid,
            description=description,
            end=end,
            keyword=keyword,
            modified=modified,
            name=name,
            name_exact=name_exact,
            o=o,
            organization_group_uuid=organization_group_uuid,
            page=page,
            page_size=page_size,
            parent_uuid=parent_uuid,
            project_uuid=project_uuid,
            resource_customer_uuid=resource_customer_uuid,
            resource_project_uuid=resource_project_uuid,
            scope_uuid=scope_uuid,
            service_manager_uuid=service_manager_uuid,
            shared=shared,
            start=start,
            state=state,
            type_=type_,
            uuid_list=uuid_list,
        )
    ).parsed
