from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_service_account import CustomerServiceAccount
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    email: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["customer"] = customer

    json_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(customer_uuid, Unset):
        json_customer_uuid = str(customer_uuid)
    params["customer_uuid"] = json_customer_uuid

    params["email"] = email

    params["page"] = page

    params["page_size"] = page_size

    params["username"] = username

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-customer-service-accounts/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["CustomerServiceAccount"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CustomerServiceAccount.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CustomerServiceAccount"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    email: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> Response[list["CustomerServiceAccount"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        email (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CustomerServiceAccount']]
    """

    kwargs = _get_kwargs(
        customer=customer,
        customer_uuid=customer_uuid,
        email=email,
        page=page,
        page_size=page_size,
        username=username,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    email: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> list["CustomerServiceAccount"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        email (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CustomerServiceAccount']
    """

    return sync_detailed(
        client=client,
        customer=customer,
        customer_uuid=customer_uuid,
        email=email,
        page=page,
        page_size=page_size,
        username=username,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    email: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> Response[list["CustomerServiceAccount"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        email (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CustomerServiceAccount']]
    """

    kwargs = _get_kwargs(
        customer=customer,
        customer_uuid=customer_uuid,
        email=email,
        page=page,
        page_size=page_size,
        username=username,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    email: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> list["CustomerServiceAccount"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        email (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CustomerServiceAccount']
    """

    return (
        await asyncio_detailed(
            client=client,
            customer=customer,
            customer_uuid=customer_uuid,
            email=email,
            page=page,
            page_size=page_size,
            username=username,
        )
    ).parsed
