import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.marketplace_provider_resources_list_field_item import MarketplaceProviderResourcesListFieldItem
from ...models.marketplace_provider_resources_list_o_item import MarketplaceProviderResourcesListOItem
from ...models.marketplace_provider_resources_list_state_item import MarketplaceProviderResourcesListStateItem
from ...models.resource import Resource
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    backend_id: Union[Unset, str] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    downscaled: Union[Unset, bool] = UNSET,
    field: Union[Unset, list[MarketplaceProviderResourcesListFieldItem]] = UNSET,
    has_terminate_date: Union[Unset, bool] = UNSET,
    lexis_links_supported: Union[Unset, bool] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderResourcesListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_billable: Union[Unset, UUID] = UNSET,
    offering_shared: Union[Unset, bool] = UNSET,
    offering_slug: Union[Unset, list[str]] = UNSET,
    offering_type: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_offering_uuid: Union[Unset, UUID] = UNSET,
    paused: Union[Unset, bool] = UNSET,
    project_name: Union[Unset, str] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    provider_uuid: Union[Unset, UUID] = UNSET,
    query: Union[Unset, str] = UNSET,
    restrict_member_access: Union[Unset, bool] = UNSET,
    runtime_state: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProviderResourcesListStateItem]] = UNSET,
    visible_to_username: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["backend_id"] = backend_id

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

    params["downscaled"] = downscaled

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["has_terminate_date"] = has_terminate_date

    params["lexis_links_supported"] = lexis_links_supported

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

    params["offering"] = offering

    json_offering_billable: Union[Unset, str] = UNSET
    if not isinstance(offering_billable, Unset):
        json_offering_billable = str(offering_billable)
    params["offering_billable"] = json_offering_billable

    params["offering_shared"] = offering_shared

    json_offering_slug: Union[Unset, list[str]] = UNSET
    if not isinstance(offering_slug, Unset):
        json_offering_slug = offering_slug

    params["offering_slug"] = json_offering_slug

    params["offering_type"] = offering_type

    json_offering_uuid: Union[Unset, list[str]] = UNSET
    if not isinstance(offering_uuid, Unset):
        json_offering_uuid = []
        for offering_uuid_item_data in offering_uuid:
            offering_uuid_item = str(offering_uuid_item_data)
            json_offering_uuid.append(offering_uuid_item)

    params["offering_uuid"] = json_offering_uuid

    params["page"] = page

    params["page_size"] = page_size

    json_parent_offering_uuid: Union[Unset, str] = UNSET
    if not isinstance(parent_offering_uuid, Unset):
        json_parent_offering_uuid = str(parent_offering_uuid)
    params["parent_offering_uuid"] = json_parent_offering_uuid

    params["paused"] = paused

    params["project_name"] = project_name

    json_project_uuid: Union[Unset, str] = UNSET
    if not isinstance(project_uuid, Unset):
        json_project_uuid = str(project_uuid)
    params["project_uuid"] = json_project_uuid

    json_provider_uuid: Union[Unset, str] = UNSET
    if not isinstance(provider_uuid, Unset):
        json_provider_uuid = str(provider_uuid)
    params["provider_uuid"] = json_provider_uuid

    params["query"] = query

    params["restrict_member_access"] = restrict_member_access

    params["runtime_state"] = runtime_state

    json_service_manager_uuid: Union[Unset, str] = UNSET
    if not isinstance(service_manager_uuid, Unset):
        json_service_manager_uuid = str(service_manager_uuid)
    params["service_manager_uuid"] = json_service_manager_uuid

    json_state: Union[Unset, list[str]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    params["visible_to_username"] = visible_to_username

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-provider-resources/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["Resource"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Resource.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Resource"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    downscaled: Union[Unset, bool] = UNSET,
    field: Union[Unset, list[MarketplaceProviderResourcesListFieldItem]] = UNSET,
    has_terminate_date: Union[Unset, bool] = UNSET,
    lexis_links_supported: Union[Unset, bool] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderResourcesListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_billable: Union[Unset, UUID] = UNSET,
    offering_shared: Union[Unset, bool] = UNSET,
    offering_slug: Union[Unset, list[str]] = UNSET,
    offering_type: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_offering_uuid: Union[Unset, UUID] = UNSET,
    paused: Union[Unset, bool] = UNSET,
    project_name: Union[Unset, str] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    provider_uuid: Union[Unset, UUID] = UNSET,
    query: Union[Unset, str] = UNSET,
    restrict_member_access: Union[Unset, bool] = UNSET,
    runtime_state: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProviderResourcesListStateItem]] = UNSET,
    visible_to_username: Union[Unset, str] = UNSET,
) -> Response[list["Resource"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        downscaled (Union[Unset, bool]):
        field (Union[Unset, list[MarketplaceProviderResourcesListFieldItem]]):
        has_terminate_date (Union[Unset, bool]):
        lexis_links_supported (Union[Unset, bool]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderResourcesListOItem]]):
        offering (Union[Unset, str]):
        offering_billable (Union[Unset, UUID]):
        offering_shared (Union[Unset, bool]):
        offering_slug (Union[Unset, list[str]]):
        offering_type (Union[Unset, str]):
        offering_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_offering_uuid (Union[Unset, UUID]):
        paused (Union[Unset, bool]):
        project_name (Union[Unset, str]):
        project_uuid (Union[Unset, UUID]):
        provider_uuid (Union[Unset, UUID]):
        query (Union[Unset, str]):
        restrict_member_access (Union[Unset, bool]):
        runtime_state (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProviderResourcesListStateItem]]):
        visible_to_username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Resource']]
    """

    kwargs = _get_kwargs(
        backend_id=backend_id,
        category_uuid=category_uuid,
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        downscaled=downscaled,
        field=field,
        has_terminate_date=has_terminate_date,
        lexis_links_supported=lexis_links_supported,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        offering=offering,
        offering_billable=offering_billable,
        offering_shared=offering_shared,
        offering_slug=offering_slug,
        offering_type=offering_type,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        parent_offering_uuid=parent_offering_uuid,
        paused=paused,
        project_name=project_name,
        project_uuid=project_uuid,
        provider_uuid=provider_uuid,
        query=query,
        restrict_member_access=restrict_member_access,
        runtime_state=runtime_state,
        service_manager_uuid=service_manager_uuid,
        state=state,
        visible_to_username=visible_to_username,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    downscaled: Union[Unset, bool] = UNSET,
    field: Union[Unset, list[MarketplaceProviderResourcesListFieldItem]] = UNSET,
    has_terminate_date: Union[Unset, bool] = UNSET,
    lexis_links_supported: Union[Unset, bool] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderResourcesListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_billable: Union[Unset, UUID] = UNSET,
    offering_shared: Union[Unset, bool] = UNSET,
    offering_slug: Union[Unset, list[str]] = UNSET,
    offering_type: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_offering_uuid: Union[Unset, UUID] = UNSET,
    paused: Union[Unset, bool] = UNSET,
    project_name: Union[Unset, str] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    provider_uuid: Union[Unset, UUID] = UNSET,
    query: Union[Unset, str] = UNSET,
    restrict_member_access: Union[Unset, bool] = UNSET,
    runtime_state: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProviderResourcesListStateItem]] = UNSET,
    visible_to_username: Union[Unset, str] = UNSET,
) -> list["Resource"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        downscaled (Union[Unset, bool]):
        field (Union[Unset, list[MarketplaceProviderResourcesListFieldItem]]):
        has_terminate_date (Union[Unset, bool]):
        lexis_links_supported (Union[Unset, bool]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderResourcesListOItem]]):
        offering (Union[Unset, str]):
        offering_billable (Union[Unset, UUID]):
        offering_shared (Union[Unset, bool]):
        offering_slug (Union[Unset, list[str]]):
        offering_type (Union[Unset, str]):
        offering_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_offering_uuid (Union[Unset, UUID]):
        paused (Union[Unset, bool]):
        project_name (Union[Unset, str]):
        project_uuid (Union[Unset, UUID]):
        provider_uuid (Union[Unset, UUID]):
        query (Union[Unset, str]):
        restrict_member_access (Union[Unset, bool]):
        runtime_state (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProviderResourcesListStateItem]]):
        visible_to_username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Resource']
    """

    return sync_detailed(
        client=client,
        backend_id=backend_id,
        category_uuid=category_uuid,
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        downscaled=downscaled,
        field=field,
        has_terminate_date=has_terminate_date,
        lexis_links_supported=lexis_links_supported,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        offering=offering,
        offering_billable=offering_billable,
        offering_shared=offering_shared,
        offering_slug=offering_slug,
        offering_type=offering_type,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        parent_offering_uuid=parent_offering_uuid,
        paused=paused,
        project_name=project_name,
        project_uuid=project_uuid,
        provider_uuid=provider_uuid,
        query=query,
        restrict_member_access=restrict_member_access,
        runtime_state=runtime_state,
        service_manager_uuid=service_manager_uuid,
        state=state,
        visible_to_username=visible_to_username,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    downscaled: Union[Unset, bool] = UNSET,
    field: Union[Unset, list[MarketplaceProviderResourcesListFieldItem]] = UNSET,
    has_terminate_date: Union[Unset, bool] = UNSET,
    lexis_links_supported: Union[Unset, bool] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderResourcesListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_billable: Union[Unset, UUID] = UNSET,
    offering_shared: Union[Unset, bool] = UNSET,
    offering_slug: Union[Unset, list[str]] = UNSET,
    offering_type: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_offering_uuid: Union[Unset, UUID] = UNSET,
    paused: Union[Unset, bool] = UNSET,
    project_name: Union[Unset, str] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    provider_uuid: Union[Unset, UUID] = UNSET,
    query: Union[Unset, str] = UNSET,
    restrict_member_access: Union[Unset, bool] = UNSET,
    runtime_state: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProviderResourcesListStateItem]] = UNSET,
    visible_to_username: Union[Unset, str] = UNSET,
) -> Response[list["Resource"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        downscaled (Union[Unset, bool]):
        field (Union[Unset, list[MarketplaceProviderResourcesListFieldItem]]):
        has_terminate_date (Union[Unset, bool]):
        lexis_links_supported (Union[Unset, bool]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderResourcesListOItem]]):
        offering (Union[Unset, str]):
        offering_billable (Union[Unset, UUID]):
        offering_shared (Union[Unset, bool]):
        offering_slug (Union[Unset, list[str]]):
        offering_type (Union[Unset, str]):
        offering_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_offering_uuid (Union[Unset, UUID]):
        paused (Union[Unset, bool]):
        project_name (Union[Unset, str]):
        project_uuid (Union[Unset, UUID]):
        provider_uuid (Union[Unset, UUID]):
        query (Union[Unset, str]):
        restrict_member_access (Union[Unset, bool]):
        runtime_state (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProviderResourcesListStateItem]]):
        visible_to_username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Resource']]
    """

    kwargs = _get_kwargs(
        backend_id=backend_id,
        category_uuid=category_uuid,
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        downscaled=downscaled,
        field=field,
        has_terminate_date=has_terminate_date,
        lexis_links_supported=lexis_links_supported,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        offering=offering,
        offering_billable=offering_billable,
        offering_shared=offering_shared,
        offering_slug=offering_slug,
        offering_type=offering_type,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        parent_offering_uuid=parent_offering_uuid,
        paused=paused,
        project_name=project_name,
        project_uuid=project_uuid,
        provider_uuid=provider_uuid,
        query=query,
        restrict_member_access=restrict_member_access,
        runtime_state=runtime_state,
        service_manager_uuid=service_manager_uuid,
        state=state,
        visible_to_username=visible_to_username,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    category_uuid: Union[Unset, UUID] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    downscaled: Union[Unset, bool] = UNSET,
    field: Union[Unset, list[MarketplaceProviderResourcesListFieldItem]] = UNSET,
    has_terminate_date: Union[Unset, bool] = UNSET,
    lexis_links_supported: Union[Unset, bool] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[MarketplaceProviderResourcesListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_billable: Union[Unset, UUID] = UNSET,
    offering_shared: Union[Unset, bool] = UNSET,
    offering_slug: Union[Unset, list[str]] = UNSET,
    offering_type: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, list[UUID]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    parent_offering_uuid: Union[Unset, UUID] = UNSET,
    paused: Union[Unset, bool] = UNSET,
    project_name: Union[Unset, str] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    provider_uuid: Union[Unset, UUID] = UNSET,
    query: Union[Unset, str] = UNSET,
    restrict_member_access: Union[Unset, bool] = UNSET,
    runtime_state: Union[Unset, str] = UNSET,
    service_manager_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProviderResourcesListStateItem]] = UNSET,
    visible_to_username: Union[Unset, str] = UNSET,
) -> list["Resource"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        category_uuid (Union[Unset, UUID]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        downscaled (Union[Unset, bool]):
        field (Union[Unset, list[MarketplaceProviderResourcesListFieldItem]]):
        has_terminate_date (Union[Unset, bool]):
        lexis_links_supported (Union[Unset, bool]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[MarketplaceProviderResourcesListOItem]]):
        offering (Union[Unset, str]):
        offering_billable (Union[Unset, UUID]):
        offering_shared (Union[Unset, bool]):
        offering_slug (Union[Unset, list[str]]):
        offering_type (Union[Unset, str]):
        offering_uuid (Union[Unset, list[UUID]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        parent_offering_uuid (Union[Unset, UUID]):
        paused (Union[Unset, bool]):
        project_name (Union[Unset, str]):
        project_uuid (Union[Unset, UUID]):
        provider_uuid (Union[Unset, UUID]):
        query (Union[Unset, str]):
        restrict_member_access (Union[Unset, bool]):
        runtime_state (Union[Unset, str]):
        service_manager_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProviderResourcesListStateItem]]):
        visible_to_username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Resource']
    """

    return (
        await asyncio_detailed(
            client=client,
            backend_id=backend_id,
            category_uuid=category_uuid,
            created=created,
            customer=customer,
            customer_uuid=customer_uuid,
            downscaled=downscaled,
            field=field,
            has_terminate_date=has_terminate_date,
            lexis_links_supported=lexis_links_supported,
            modified=modified,
            name=name,
            name_exact=name_exact,
            o=o,
            offering=offering,
            offering_billable=offering_billable,
            offering_shared=offering_shared,
            offering_slug=offering_slug,
            offering_type=offering_type,
            offering_uuid=offering_uuid,
            page=page,
            page_size=page_size,
            parent_offering_uuid=parent_offering_uuid,
            paused=paused,
            project_name=project_name,
            project_uuid=project_uuid,
            provider_uuid=provider_uuid,
            query=query,
            restrict_member_access=restrict_member_access,
            runtime_state=runtime_state,
            service_manager_uuid=service_manager_uuid,
            state=state,
            visible_to_username=visible_to_username,
        )
    ).parsed
