from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.marketplace_provider_customer import MarketplaceProviderCustomer
from ...models.marketplace_service_providers_user_customers_list_field_item import (
    MarketplaceServiceProvidersUserCustomersListFieldItem,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    service_provider_uuid: UUID,
    *,
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    field: Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
    user_uuid: UUID,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["abbreviation"] = abbreviation

    params["agreement_number"] = agreement_number

    params["archived"] = archived

    params["backend_id"] = backend_id

    params["contact_details"] = contact_details

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["name"] = name

    params["name_exact"] = name_exact

    params["native_name"] = native_name

    params["organization_group_name"] = organization_group_name

    json_organization_group_uuid: Union[Unset, list[str]] = UNSET
    if not isinstance(organization_group_uuid, Unset):
        json_organization_group_uuid = []
        for organization_group_uuid_item_data in organization_group_uuid:
            organization_group_uuid_item = str(organization_group_uuid_item_data)
            json_organization_group_uuid.append(organization_group_uuid_item)

    params["organization_group_uuid"] = json_organization_group_uuid

    params["owned_by_current_user"] = owned_by_current_user

    params["page"] = page

    params["page_size"] = page_size

    params["query"] = query

    params["registration_code"] = registration_code

    json_user_uuid = str(user_uuid)
    params["user_uuid"] = json_user_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/marketplace-service-providers/{service_provider_uuid}/user_customers/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["MarketplaceProviderCustomer"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = MarketplaceProviderCustomer.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["MarketplaceProviderCustomer"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    field: Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
    user_uuid: UUID,
) -> Response[list["MarketplaceProviderCustomer"]]:
    """Return customers that have access role for a specified user within service provider's scope.

            Checks for:
            - Customers where user has direct permissions
            - Customers with projects where user has project roles
            - Customers related to service provider's resources

            If user UUID is invalid or missing, returns empty list.

    Args:
        service_provider_uuid (UUID):
        abbreviation (Union[Unset, str]):
        agreement_number (Union[Unset, str]):
        archived (Union[Unset, bool]):
        backend_id (Union[Unset, str]):
        contact_details (Union[Unset, str]):
        field (Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        native_name (Union[Unset, str]):
        organization_group_name (Union[Unset, str]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        owned_by_current_user (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        registration_code (Union[Unset, str]):
        user_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MarketplaceProviderCustomer']]
    """

    kwargs = _get_kwargs(
        service_provider_uuid=service_provider_uuid,
        abbreviation=abbreviation,
        agreement_number=agreement_number,
        archived=archived,
        backend_id=backend_id,
        contact_details=contact_details,
        field=field,
        name=name,
        name_exact=name_exact,
        native_name=native_name,
        organization_group_name=organization_group_name,
        organization_group_uuid=organization_group_uuid,
        owned_by_current_user=owned_by_current_user,
        page=page,
        page_size=page_size,
        query=query,
        registration_code=registration_code,
        user_uuid=user_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    field: Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
    user_uuid: UUID,
) -> list["MarketplaceProviderCustomer"]:
    """Return customers that have access role for a specified user within service provider's scope.

            Checks for:
            - Customers where user has direct permissions
            - Customers with projects where user has project roles
            - Customers related to service provider's resources

            If user UUID is invalid or missing, returns empty list.

    Args:
        service_provider_uuid (UUID):
        abbreviation (Union[Unset, str]):
        agreement_number (Union[Unset, str]):
        archived (Union[Unset, bool]):
        backend_id (Union[Unset, str]):
        contact_details (Union[Unset, str]):
        field (Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        native_name (Union[Unset, str]):
        organization_group_name (Union[Unset, str]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        owned_by_current_user (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        registration_code (Union[Unset, str]):
        user_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MarketplaceProviderCustomer']
    """

    return sync_detailed(
        service_provider_uuid=service_provider_uuid,
        client=client,
        abbreviation=abbreviation,
        agreement_number=agreement_number,
        archived=archived,
        backend_id=backend_id,
        contact_details=contact_details,
        field=field,
        name=name,
        name_exact=name_exact,
        native_name=native_name,
        organization_group_name=organization_group_name,
        organization_group_uuid=organization_group_uuid,
        owned_by_current_user=owned_by_current_user,
        page=page,
        page_size=page_size,
        query=query,
        registration_code=registration_code,
        user_uuid=user_uuid,
    ).parsed


async def asyncio_detailed(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    field: Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
    user_uuid: UUID,
) -> Response[list["MarketplaceProviderCustomer"]]:
    """Return customers that have access role for a specified user within service provider's scope.

            Checks for:
            - Customers where user has direct permissions
            - Customers with projects where user has project roles
            - Customers related to service provider's resources

            If user UUID is invalid or missing, returns empty list.

    Args:
        service_provider_uuid (UUID):
        abbreviation (Union[Unset, str]):
        agreement_number (Union[Unset, str]):
        archived (Union[Unset, bool]):
        backend_id (Union[Unset, str]):
        contact_details (Union[Unset, str]):
        field (Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        native_name (Union[Unset, str]):
        organization_group_name (Union[Unset, str]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        owned_by_current_user (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        registration_code (Union[Unset, str]):
        user_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MarketplaceProviderCustomer']]
    """

    kwargs = _get_kwargs(
        service_provider_uuid=service_provider_uuid,
        abbreviation=abbreviation,
        agreement_number=agreement_number,
        archived=archived,
        backend_id=backend_id,
        contact_details=contact_details,
        field=field,
        name=name,
        name_exact=name_exact,
        native_name=native_name,
        organization_group_name=organization_group_name,
        organization_group_uuid=organization_group_uuid,
        owned_by_current_user=owned_by_current_user,
        page=page,
        page_size=page_size,
        query=query,
        registration_code=registration_code,
        user_uuid=user_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    service_provider_uuid: UUID,
    *,
    client: AuthenticatedClient,
    abbreviation: Union[Unset, str] = UNSET,
    agreement_number: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    backend_id: Union[Unset, str] = UNSET,
    contact_details: Union[Unset, str] = UNSET,
    field: Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    organization_group_name: Union[Unset, str] = UNSET,
    organization_group_uuid: Union[Unset, list[UUID]] = UNSET,
    owned_by_current_user: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    registration_code: Union[Unset, str] = UNSET,
    user_uuid: UUID,
) -> list["MarketplaceProviderCustomer"]:
    """Return customers that have access role for a specified user within service provider's scope.

            Checks for:
            - Customers where user has direct permissions
            - Customers with projects where user has project roles
            - Customers related to service provider's resources

            If user UUID is invalid or missing, returns empty list.

    Args:
        service_provider_uuid (UUID):
        abbreviation (Union[Unset, str]):
        agreement_number (Union[Unset, str]):
        archived (Union[Unset, bool]):
        backend_id (Union[Unset, str]):
        contact_details (Union[Unset, str]):
        field (Union[Unset, list[MarketplaceServiceProvidersUserCustomersListFieldItem]]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        native_name (Union[Unset, str]):
        organization_group_name (Union[Unset, str]):
        organization_group_uuid (Union[Unset, list[UUID]]):
        owned_by_current_user (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        registration_code (Union[Unset, str]):
        user_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MarketplaceProviderCustomer']
    """

    return (
        await asyncio_detailed(
            service_provider_uuid=service_provider_uuid,
            client=client,
            abbreviation=abbreviation,
            agreement_number=agreement_number,
            archived=archived,
            backend_id=backend_id,
            contact_details=contact_details,
            field=field,
            name=name,
            name_exact=name_exact,
            native_name=native_name,
            organization_group_name=organization_group_name,
            organization_group_uuid=organization_group_uuid,
            owned_by_current_user=owned_by_current_user,
            page=page,
            page_size=page_size,
            query=query,
            registration_code=registration_code,
            user_uuid=user_uuid,
        )
    ).parsed
