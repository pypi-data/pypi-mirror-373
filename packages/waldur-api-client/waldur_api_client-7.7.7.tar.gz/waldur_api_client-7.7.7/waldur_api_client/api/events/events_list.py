from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.event import Event
from ...models.events_list_field_item import EventsListFieldItem
from ...models.events_list_o_item import EventsListOItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    created_from: Union[Unset, float] = UNSET,
    created_to: Union[Unset, float] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    field: Union[Unset, list[EventsListFieldItem]] = UNSET,
    message: Union[Unset, str] = UNSET,
    o: Union[Unset, list[EventsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["created_from"] = created_from

    params["created_to"] = created_to

    json_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(customer_uuid, Unset):
        json_customer_uuid = str(customer_uuid)
    params["customer_uuid"] = json_customer_uuid

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["message"] = message

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_project_uuid: Union[Unset, str] = UNSET
    if not isinstance(project_uuid, Unset):
        json_project_uuid = str(project_uuid)
    params["project_uuid"] = json_project_uuid

    json_user_uuid: Union[Unset, str] = UNSET
    if not isinstance(user_uuid, Unset):
        json_user_uuid = str(user_uuid)
    params["user_uuid"] = json_user_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/events/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["Event"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Event.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[list["Event"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    created_from: Union[Unset, float] = UNSET,
    created_to: Union[Unset, float] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    field: Union[Unset, list[EventsListFieldItem]] = UNSET,
    message: Union[Unset, str] = UNSET,
    o: Union[Unset, list[EventsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["Event"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created_from (Union[Unset, float]):
        created_to (Union[Unset, float]):
        customer_uuid (Union[Unset, UUID]):
        field (Union[Unset, list[EventsListFieldItem]]):
        message (Union[Unset, str]):
        o (Union[Unset, list[EventsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        user_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Event']]
    """

    kwargs = _get_kwargs(
        created_from=created_from,
        created_to=created_to,
        customer_uuid=customer_uuid,
        field=field,
        message=message,
        o=o,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        user_uuid=user_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    created_from: Union[Unset, float] = UNSET,
    created_to: Union[Unset, float] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    field: Union[Unset, list[EventsListFieldItem]] = UNSET,
    message: Union[Unset, str] = UNSET,
    o: Union[Unset, list[EventsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
) -> list["Event"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created_from (Union[Unset, float]):
        created_to (Union[Unset, float]):
        customer_uuid (Union[Unset, UUID]):
        field (Union[Unset, list[EventsListFieldItem]]):
        message (Union[Unset, str]):
        o (Union[Unset, list[EventsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        user_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Event']
    """

    return sync_detailed(
        client=client,
        created_from=created_from,
        created_to=created_to,
        customer_uuid=customer_uuid,
        field=field,
        message=message,
        o=o,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        user_uuid=user_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    created_from: Union[Unset, float] = UNSET,
    created_to: Union[Unset, float] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    field: Union[Unset, list[EventsListFieldItem]] = UNSET,
    message: Union[Unset, str] = UNSET,
    o: Union[Unset, list[EventsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["Event"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created_from (Union[Unset, float]):
        created_to (Union[Unset, float]):
        customer_uuid (Union[Unset, UUID]):
        field (Union[Unset, list[EventsListFieldItem]]):
        message (Union[Unset, str]):
        o (Union[Unset, list[EventsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        user_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Event']]
    """

    kwargs = _get_kwargs(
        created_from=created_from,
        created_to=created_to,
        customer_uuid=customer_uuid,
        field=field,
        message=message,
        o=o,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        user_uuid=user_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    created_from: Union[Unset, float] = UNSET,
    created_to: Union[Unset, float] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    field: Union[Unset, list[EventsListFieldItem]] = UNSET,
    message: Union[Unset, str] = UNSET,
    o: Union[Unset, list[EventsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
) -> list["Event"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created_from (Union[Unset, float]):
        created_to (Union[Unset, float]):
        customer_uuid (Union[Unset, UUID]):
        field (Union[Unset, list[EventsListFieldItem]]):
        message (Union[Unset, str]):
        o (Union[Unset, list[EventsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        user_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Event']
    """

    return (
        await asyncio_detailed(
            client=client,
            created_from=created_from,
            created_to=created_to,
            customer_uuid=customer_uuid,
            field=field,
            message=message,
            o=o,
            page=page,
            page_size=page_size,
            project_uuid=project_uuid,
            user_uuid=user_uuid,
        )
    ).parsed
