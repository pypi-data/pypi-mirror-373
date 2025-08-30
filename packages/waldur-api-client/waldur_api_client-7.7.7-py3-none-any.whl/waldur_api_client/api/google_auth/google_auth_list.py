from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.google_auth_list_field_item import GoogleAuthListFieldItem
from ...models.google_credentials import GoogleCredentials
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    field: Union[Unset, list[GoogleAuthListFieldItem]] = UNSET,
    has_credentials: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["has_credentials"] = has_credentials

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/google-auth/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["GoogleCredentials"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GoogleCredentials.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["GoogleCredentials"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    field: Union[Unset, list[GoogleAuthListFieldItem]] = UNSET,
    has_credentials: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[list["GoogleCredentials"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        field (Union[Unset, list[GoogleAuthListFieldItem]]):
        has_credentials (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GoogleCredentials']]
    """

    kwargs = _get_kwargs(
        field=field,
        has_credentials=has_credentials,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    field: Union[Unset, list[GoogleAuthListFieldItem]] = UNSET,
    has_credentials: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> list["GoogleCredentials"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        field (Union[Unset, list[GoogleAuthListFieldItem]]):
        has_credentials (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GoogleCredentials']
    """

    return sync_detailed(
        client=client,
        field=field,
        has_credentials=has_credentials,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    field: Union[Unset, list[GoogleAuthListFieldItem]] = UNSET,
    has_credentials: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[list["GoogleCredentials"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        field (Union[Unset, list[GoogleAuthListFieldItem]]):
        has_credentials (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['GoogleCredentials']]
    """

    kwargs = _get_kwargs(
        field=field,
        has_credentials=has_credentials,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    field: Union[Unset, list[GoogleAuthListFieldItem]] = UNSET,
    has_credentials: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> list["GoogleCredentials"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        field (Union[Unset, list[GoogleAuthListFieldItem]]):
        has_credentials (Union[Unset, bool]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['GoogleCredentials']
    """

    return (
        await asyncio_detailed(
            client=client,
            field=field,
            has_credentials=has_credentials,
            page=page,
            page_size=page_size,
        )
    ).parsed
