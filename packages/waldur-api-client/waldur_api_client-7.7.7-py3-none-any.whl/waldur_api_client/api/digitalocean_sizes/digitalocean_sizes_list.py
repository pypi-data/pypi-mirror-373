from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.digital_ocean_size import DigitalOceanSize
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    cores: Union[Unset, int] = UNSET,
    disk: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    ram: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["cores"] = cores

    params["disk"] = disk

    params["name"] = name

    params["name_exact"] = name_exact

    params["page"] = page

    params["page_size"] = page_size

    params["ram"] = ram

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/digitalocean-sizes/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["DigitalOceanSize"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DigitalOceanSize.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["DigitalOceanSize"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    cores: Union[Unset, int] = UNSET,
    disk: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    ram: Union[Unset, int] = UNSET,
) -> Response[list["DigitalOceanSize"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        cores (Union[Unset, int]):
        disk (Union[Unset, int]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        ram (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['DigitalOceanSize']]
    """

    kwargs = _get_kwargs(
        cores=cores,
        disk=disk,
        name=name,
        name_exact=name_exact,
        page=page,
        page_size=page_size,
        ram=ram,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    cores: Union[Unset, int] = UNSET,
    disk: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    ram: Union[Unset, int] = UNSET,
) -> list["DigitalOceanSize"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        cores (Union[Unset, int]):
        disk (Union[Unset, int]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        ram (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['DigitalOceanSize']
    """

    return sync_detailed(
        client=client,
        cores=cores,
        disk=disk,
        name=name,
        name_exact=name_exact,
        page=page,
        page_size=page_size,
        ram=ram,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    cores: Union[Unset, int] = UNSET,
    disk: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    ram: Union[Unset, int] = UNSET,
) -> Response[list["DigitalOceanSize"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        cores (Union[Unset, int]):
        disk (Union[Unset, int]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        ram (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['DigitalOceanSize']]
    """

    kwargs = _get_kwargs(
        cores=cores,
        disk=disk,
        name=name,
        name_exact=name_exact,
        page=page,
        page_size=page_size,
        ram=ram,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    cores: Union[Unset, int] = UNSET,
    disk: Union[Unset, int] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    ram: Union[Unset, int] = UNSET,
) -> list["DigitalOceanSize"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        cores (Union[Unset, int]):
        disk (Union[Unset, int]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        ram (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['DigitalOceanSize']
    """

    return (
        await asyncio_detailed(
            client=client,
            cores=cores,
            disk=disk,
            name=name,
            name_exact=name_exact,
            page=page,
            page_size=page_size,
            ram=ram,
        )
    ).parsed
