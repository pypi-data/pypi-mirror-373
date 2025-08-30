from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.event_subscription import EventSubscription
from ...models.event_subscriptions_list_o_item import EventSubscriptionsListOItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    o: Union[Unset, list[EventSubscriptionsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user_username: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    params["user_username"] = user_username

    params["user_uuid"] = user_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/event-subscriptions/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["EventSubscription"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = EventSubscription.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["EventSubscription"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    o: Union[Unset, list[EventSubscriptionsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user_username: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, str] = UNSET,
) -> Response[list["EventSubscription"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        o (Union[Unset, list[EventSubscriptionsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user_username (Union[Unset, str]):
        user_uuid (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['EventSubscription']]
    """

    kwargs = _get_kwargs(
        o=o,
        page=page,
        page_size=page_size,
        user_username=user_username,
        user_uuid=user_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    o: Union[Unset, list[EventSubscriptionsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user_username: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, str] = UNSET,
) -> list["EventSubscription"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        o (Union[Unset, list[EventSubscriptionsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user_username (Union[Unset, str]):
        user_uuid (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['EventSubscription']
    """

    return sync_detailed(
        client=client,
        o=o,
        page=page,
        page_size=page_size,
        user_username=user_username,
        user_uuid=user_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    o: Union[Unset, list[EventSubscriptionsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user_username: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, str] = UNSET,
) -> Response[list["EventSubscription"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        o (Union[Unset, list[EventSubscriptionsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user_username (Union[Unset, str]):
        user_uuid (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['EventSubscription']]
    """

    kwargs = _get_kwargs(
        o=o,
        page=page,
        page_size=page_size,
        user_username=user_username,
        user_uuid=user_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    o: Union[Unset, list[EventSubscriptionsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    user_username: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, str] = UNSET,
) -> list["EventSubscription"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        o (Union[Unset, list[EventSubscriptionsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        user_username (Union[Unset, str]):
        user_uuid (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['EventSubscription']
    """

    return (
        await asyncio_detailed(
            client=client,
            o=o,
            page=page,
            page_size=page_size,
            user_username=user_username,
            user_uuid=user_uuid,
        )
    ).parsed
