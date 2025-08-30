from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.admin_announcement import AdminAnnouncement
from ...models.admin_announcements_list_field_item import AdminAnnouncementsListFieldItem
from ...models.admin_announcements_list_o_item import AdminAnnouncementsListOItem
from ...models.admin_announcements_list_type_item import AdminAnnouncementsListTypeItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[AdminAnnouncementsListFieldItem]] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsListTypeItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["description"] = description

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["is_active"] = is_active

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_type_: Union[Unset, list[str]] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = []
        for type_item_data in type_:
            type_item = type_item_data.value
            json_type_.append(type_item)

    params["type"] = json_type_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/admin-announcements/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["AdminAnnouncement"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AdminAnnouncement.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["AdminAnnouncement"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[AdminAnnouncementsListFieldItem]] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsListTypeItem]] = UNSET,
) -> Response[list["AdminAnnouncement"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        description (Union[Unset, str]):
        field (Union[Unset, list[AdminAnnouncementsListFieldItem]]):
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[AdminAnnouncementsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        type_ (Union[Unset, list[AdminAnnouncementsListTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AdminAnnouncement']]
    """

    kwargs = _get_kwargs(
        description=description,
        field=field,
        is_active=is_active,
        o=o,
        page=page,
        page_size=page_size,
        type_=type_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[AdminAnnouncementsListFieldItem]] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsListTypeItem]] = UNSET,
) -> list["AdminAnnouncement"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        description (Union[Unset, str]):
        field (Union[Unset, list[AdminAnnouncementsListFieldItem]]):
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[AdminAnnouncementsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        type_ (Union[Unset, list[AdminAnnouncementsListTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AdminAnnouncement']
    """

    return sync_detailed(
        client=client,
        description=description,
        field=field,
        is_active=is_active,
        o=o,
        page=page,
        page_size=page_size,
        type_=type_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[AdminAnnouncementsListFieldItem]] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsListTypeItem]] = UNSET,
) -> Response[list["AdminAnnouncement"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        description (Union[Unset, str]):
        field (Union[Unset, list[AdminAnnouncementsListFieldItem]]):
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[AdminAnnouncementsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        type_ (Union[Unset, list[AdminAnnouncementsListTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['AdminAnnouncement']]
    """

    kwargs = _get_kwargs(
        description=description,
        field=field,
        is_active=is_active,
        o=o,
        page=page,
        page_size=page_size,
        type_=type_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[AdminAnnouncementsListFieldItem]] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[AdminAnnouncementsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    type_: Union[Unset, list[AdminAnnouncementsListTypeItem]] = UNSET,
) -> list["AdminAnnouncement"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        description (Union[Unset, str]):
        field (Union[Unset, list[AdminAnnouncementsListFieldItem]]):
        is_active (Union[Unset, bool]):
        o (Union[Unset, list[AdminAnnouncementsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        type_ (Union[Unset, list[AdminAnnouncementsListTypeItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['AdminAnnouncement']
    """

    return (
        await asyncio_detailed(
            client=client,
            description=description,
            field=field,
            is_active=is_active,
            o=o,
            page=page,
            page_size=page_size,
            type_=type_,
        )
    ).parsed
