from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.migration_details import MigrationDetails
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    dst_resource_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    src_resource_uuid: Union[Unset, UUID] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_dst_resource_uuid: Union[Unset, str] = UNSET
    if not isinstance(dst_resource_uuid, Unset):
        json_dst_resource_uuid = str(dst_resource_uuid)
    params["dst_resource_uuid"] = json_dst_resource_uuid

    params["page"] = page

    params["page_size"] = page_size

    json_src_resource_uuid: Union[Unset, str] = UNSET
    if not isinstance(src_resource_uuid, Unset):
        json_src_resource_uuid = str(src_resource_uuid)
    params["src_resource_uuid"] = json_src_resource_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/openstack-migrations/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["MigrationDetails"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = MigrationDetails.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["MigrationDetails"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    dst_resource_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    src_resource_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["MigrationDetails"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        dst_resource_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        src_resource_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MigrationDetails']]
    """

    kwargs = _get_kwargs(
        dst_resource_uuid=dst_resource_uuid,
        page=page,
        page_size=page_size,
        src_resource_uuid=src_resource_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    dst_resource_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    src_resource_uuid: Union[Unset, UUID] = UNSET,
) -> list["MigrationDetails"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        dst_resource_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        src_resource_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MigrationDetails']
    """

    return sync_detailed(
        client=client,
        dst_resource_uuid=dst_resource_uuid,
        page=page,
        page_size=page_size,
        src_resource_uuid=src_resource_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    dst_resource_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    src_resource_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["MigrationDetails"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        dst_resource_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        src_resource_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['MigrationDetails']]
    """

    kwargs = _get_kwargs(
        dst_resource_uuid=dst_resource_uuid,
        page=page,
        page_size=page_size,
        src_resource_uuid=src_resource_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    dst_resource_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    src_resource_uuid: Union[Unset, UUID] = UNSET,
) -> list["MigrationDetails"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        dst_resource_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        src_resource_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['MigrationDetails']
    """

    return (
        await asyncio_detailed(
            client=client,
            dst_resource_uuid=dst_resource_uuid,
            page=page,
            page_size=page_size,
            src_resource_uuid=src_resource_uuid,
        )
    ).parsed
