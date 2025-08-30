from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.category_column import CategoryColumn
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    category_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_category_uuid: Union[Unset, str] = UNSET
    if not isinstance(category_uuid, Unset):
        json_category_uuid = str(category_uuid)
    params["category_uuid"] = json_category_uuid

    params["page"] = page

    params["page_size"] = page_size

    params["title"] = title

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-category-columns/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["CategoryColumn"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CategoryColumn.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CategoryColumn"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    category_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> Response[list["CategoryColumn"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        category_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CategoryColumn']]
    """

    kwargs = _get_kwargs(
        category_uuid=category_uuid,
        page=page,
        page_size=page_size,
        title=title,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    category_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> list["CategoryColumn"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        category_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CategoryColumn']
    """

    return sync_detailed(
        client=client,
        category_uuid=category_uuid,
        page=page,
        page_size=page_size,
        title=title,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    category_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> Response[list["CategoryColumn"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        category_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CategoryColumn']]
    """

    kwargs = _get_kwargs(
        category_uuid=category_uuid,
        page=page,
        page_size=page_size,
        title=title,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    category_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> list["CategoryColumn"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        category_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CategoryColumn']
    """

    return (
        await asyncio_detailed(
            client=client,
            category_uuid=category_uuid,
            page=page,
            page_size=page_size,
            title=title,
        )
    ).parsed
