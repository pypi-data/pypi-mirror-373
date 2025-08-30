import datetime
from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.category_component_usage import CategoryComponentUsage
from ...models.marketplace_category_component_usages_list_field_item import (
    MarketplaceCategoryComponentUsagesListFieldItem,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    date_after: Union[Unset, datetime.date] = UNSET,
    date_before: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_date_after: Union[Unset, str] = UNSET
    if not isinstance(date_after, Unset):
        json_date_after = date_after.isoformat()
    params["date_after"] = json_date_after

    json_date_before: Union[Unset, str] = UNSET
    if not isinstance(date_before, Unset):
        json_date_before = date_before.isoformat()
    params["date_before"] = json_date_before

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-category-component-usages/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["CategoryComponentUsage"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CategoryComponentUsage.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CategoryComponentUsage"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    date_after: Union[Unset, datetime.date] = UNSET,
    date_before: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[list["CategoryComponentUsage"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        date_after (Union[Unset, datetime.date]):
        date_before (Union[Unset, datetime.date]):
        field (Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CategoryComponentUsage']]
    """

    kwargs = _get_kwargs(
        date_after=date_after,
        date_before=date_before,
        field=field,
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
    date_after: Union[Unset, datetime.date] = UNSET,
    date_before: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> list["CategoryComponentUsage"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        date_after (Union[Unset, datetime.date]):
        date_before (Union[Unset, datetime.date]):
        field (Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CategoryComponentUsage']
    """

    return sync_detailed(
        client=client,
        date_after=date_after,
        date_before=date_before,
        field=field,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    date_after: Union[Unset, datetime.date] = UNSET,
    date_before: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[list["CategoryComponentUsage"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        date_after (Union[Unset, datetime.date]):
        date_before (Union[Unset, datetime.date]):
        field (Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CategoryComponentUsage']]
    """

    kwargs = _get_kwargs(
        date_after=date_after,
        date_before=date_before,
        field=field,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    date_after: Union[Unset, datetime.date] = UNSET,
    date_before: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> list["CategoryComponentUsage"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        date_after (Union[Unset, datetime.date]):
        date_before (Union[Unset, datetime.date]):
        field (Union[Unset, list[MarketplaceCategoryComponentUsagesListFieldItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CategoryComponentUsage']
    """

    return (
        await asyncio_detailed(
            client=client,
            date_after=date_after,
            date_before=date_before,
            field=field,
            page=page,
            page_size=page_size,
        )
    ).parsed
