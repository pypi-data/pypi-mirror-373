from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.support_user import SupportUser
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    backend_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["backend_id"] = backend_id

    params["name"] = name

    params["page"] = page

    params["page_size"] = page_size

    params["user"] = user

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/support-users/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["SupportUser"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SupportUser.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["SupportUser"]]:
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
    name: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user: Union[Unset, int] = UNSET,
) -> Response[list["SupportUser"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        name (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['SupportUser']]
    """

    kwargs = _get_kwargs(
        backend_id=backend_id,
        name=name,
        page=page,
        page_size=page_size,
        user=user,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user: Union[Unset, int] = UNSET,
) -> list["SupportUser"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        name (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['SupportUser']
    """

    return sync_detailed(
        client=client,
        backend_id=backend_id,
        name=name,
        page=page,
        page_size=page_size,
        user=user,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user: Union[Unset, int] = UNSET,
) -> Response[list["SupportUser"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        name (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['SupportUser']]
    """

    kwargs = _get_kwargs(
        backend_id=backend_id,
        name=name,
        page=page,
        page_size=page_size,
        user=user,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user: Union[Unset, int] = UNSET,
) -> list["SupportUser"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        name (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['SupportUser']
    """

    return (
        await asyncio_detailed(
            client=client,
            backend_id=backend_id,
            name=name,
            page=page,
            page_size=page_size,
            user=user,
        )
    ).parsed
