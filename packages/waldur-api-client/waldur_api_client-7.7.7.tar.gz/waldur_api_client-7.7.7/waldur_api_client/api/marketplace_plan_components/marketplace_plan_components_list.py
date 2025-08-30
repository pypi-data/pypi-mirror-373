from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.plan_component import PlanComponent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    archived: Union[Unset, bool] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    plan_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["archived"] = archived

    json_offering_uuid: Union[Unset, str] = UNSET
    if not isinstance(offering_uuid, Unset):
        json_offering_uuid = str(offering_uuid)
    params["offering_uuid"] = json_offering_uuid

    params["page"] = page

    params["page_size"] = page_size

    json_plan_uuid: Union[Unset, str] = UNSET
    if not isinstance(plan_uuid, Unset):
        json_plan_uuid = str(plan_uuid)
    params["plan_uuid"] = json_plan_uuid

    params["shared"] = shared

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-plan-components/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["PlanComponent"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PlanComponent.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["PlanComponent"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    plan_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
) -> Response[list["PlanComponent"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        archived (Union[Unset, bool]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        plan_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['PlanComponent']]
    """

    kwargs = _get_kwargs(
        archived=archived,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        plan_uuid=plan_uuid,
        shared=shared,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    plan_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
) -> list["PlanComponent"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        archived (Union[Unset, bool]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        plan_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['PlanComponent']
    """

    return sync_detailed(
        client=client,
        archived=archived,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        plan_uuid=plan_uuid,
        shared=shared,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    plan_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
) -> Response[list["PlanComponent"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        archived (Union[Unset, bool]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        plan_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['PlanComponent']]
    """

    kwargs = _get_kwargs(
        archived=archived,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        plan_uuid=plan_uuid,
        shared=shared,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    plan_uuid: Union[Unset, UUID] = UNSET,
    shared: Union[Unset, bool] = UNSET,
) -> list["PlanComponent"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        archived (Union[Unset, bool]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        plan_uuid (Union[Unset, UUID]):
        shared (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['PlanComponent']
    """

    return (
        await asyncio_detailed(
            client=client,
            archived=archived,
            offering_uuid=offering_uuid,
            page=page,
            page_size=page_size,
            plan_uuid=plan_uuid,
            shared=shared,
        )
    ).parsed
