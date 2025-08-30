from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.name_uuid import NameUUID
from ...types import UNSET, Response, Unset


def _get_kwargs(
    uuid: UUID,
    *,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_name: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["page_size"] = page_size

    params["project_name"] = project_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/marketplace-service-providers/{uuid}/robot_account_projects/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["NameUUID"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = NameUUID.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["NameUUID"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_name: Union[Unset, str] = UNSET,
) -> Response[list["NameUUID"]]:
    """
    Args:
        uuid (UUID):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['NameUUID']]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        page=page,
        page_size=page_size,
        project_name=project_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_name: Union[Unset, str] = UNSET,
) -> list["NameUUID"]:
    """
    Args:
        uuid (UUID):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['NameUUID']
    """

    return sync_detailed(
        uuid=uuid,
        client=client,
        page=page,
        page_size=page_size,
        project_name=project_name,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_name: Union[Unset, str] = UNSET,
) -> Response[list["NameUUID"]]:
    """
    Args:
        uuid (UUID):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['NameUUID']]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        page=page,
        page_size=page_size,
        project_name=project_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    project_name: Union[Unset, str] = UNSET,
) -> list["NameUUID"]:
    """
    Args:
        uuid (UUID):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        project_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['NameUUID']
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            page=page,
            page_size=page_size,
            project_name=project_name,
        )
    ).parsed
