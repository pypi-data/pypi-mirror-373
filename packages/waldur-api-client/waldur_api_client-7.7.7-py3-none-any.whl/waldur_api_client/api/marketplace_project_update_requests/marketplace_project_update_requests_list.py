from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.marketplace_project_update_requests_list_state_item import MarketplaceProjectUpdateRequestsListStateItem
from ...models.remote_project_update_request import RemoteProjectUpdateRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    customer_uuid: Union[Unset, UUID] = UNSET,
    offering_customer_uuid: Union[Unset, UUID] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(customer_uuid, Unset):
        json_customer_uuid = str(customer_uuid)
    params["customer_uuid"] = json_customer_uuid

    json_offering_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(offering_customer_uuid, Unset):
        json_offering_customer_uuid = str(offering_customer_uuid)
    params["offering_customer_uuid"] = json_offering_customer_uuid

    json_offering_uuid: Union[Unset, str] = UNSET
    if not isinstance(offering_uuid, Unset):
        json_offering_uuid = str(offering_uuid)
    params["offering_uuid"] = json_offering_uuid

    params["page"] = page

    params["page_size"] = page_size

    json_project_uuid: Union[Unset, str] = UNSET
    if not isinstance(project_uuid, Unset):
        json_project_uuid = str(project_uuid)
    params["project_uuid"] = json_project_uuid

    json_state: Union[Unset, list[str]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-project-update-requests/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["RemoteProjectUpdateRequest"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = RemoteProjectUpdateRequest.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["RemoteProjectUpdateRequest"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    customer_uuid: Union[Unset, UUID] = UNSET,
    offering_customer_uuid: Union[Unset, UUID] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]] = UNSET,
) -> Response[list["RemoteProjectUpdateRequest"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        offering_customer_uuid (Union[Unset, UUID]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['RemoteProjectUpdateRequest']]
    """

    kwargs = _get_kwargs(
        customer_uuid=customer_uuid,
        offering_customer_uuid=offering_customer_uuid,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        state=state,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    customer_uuid: Union[Unset, UUID] = UNSET,
    offering_customer_uuid: Union[Unset, UUID] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]] = UNSET,
) -> list["RemoteProjectUpdateRequest"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        offering_customer_uuid (Union[Unset, UUID]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['RemoteProjectUpdateRequest']
    """

    return sync_detailed(
        client=client,
        customer_uuid=customer_uuid,
        offering_customer_uuid=offering_customer_uuid,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        state=state,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    customer_uuid: Union[Unset, UUID] = UNSET,
    offering_customer_uuid: Union[Unset, UUID] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]] = UNSET,
) -> Response[list["RemoteProjectUpdateRequest"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        offering_customer_uuid (Union[Unset, UUID]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['RemoteProjectUpdateRequest']]
    """

    kwargs = _get_kwargs(
        customer_uuid=customer_uuid,
        offering_customer_uuid=offering_customer_uuid,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        project_uuid=project_uuid,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    customer_uuid: Union[Unset, UUID] = UNSET,
    offering_customer_uuid: Union[Unset, UUID] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_uuid: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]] = UNSET,
) -> list["RemoteProjectUpdateRequest"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        offering_customer_uuid (Union[Unset, UUID]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_uuid (Union[Unset, UUID]):
        state (Union[Unset, list[MarketplaceProjectUpdateRequestsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['RemoteProjectUpdateRequest']
    """

    return (
        await asyncio_detailed(
            client=client,
            customer_uuid=customer_uuid,
            offering_customer_uuid=offering_customer_uuid,
            offering_uuid=offering_uuid,
            page=page,
            page_size=page_size,
            project_uuid=project_uuid,
            state=state,
        )
    ).parsed
