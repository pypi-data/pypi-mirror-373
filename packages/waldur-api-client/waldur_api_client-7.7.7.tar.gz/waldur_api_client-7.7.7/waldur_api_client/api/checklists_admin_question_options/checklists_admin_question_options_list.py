from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.question_options_admin import QuestionOptionsAdmin
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["page_size"] = page_size

    json_question_uuid: Union[Unset, str] = UNSET
    if not isinstance(question_uuid, Unset):
        json_question_uuid = str(question_uuid)
    params["question_uuid"] = json_question_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/checklists-admin-question-options/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["QuestionOptionsAdmin"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = QuestionOptionsAdmin.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["QuestionOptionsAdmin"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["QuestionOptionsAdmin"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['QuestionOptionsAdmin']]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        question_uuid=question_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> list["QuestionOptionsAdmin"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['QuestionOptionsAdmin']
    """

    return sync_detailed(
        client=client,
        page=page,
        page_size=page_size,
        question_uuid=question_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["QuestionOptionsAdmin"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['QuestionOptionsAdmin']]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        question_uuid=question_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    question_uuid: Union[Unset, UUID] = UNSET,
) -> list["QuestionOptionsAdmin"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        question_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['QuestionOptionsAdmin']
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_size=page_size,
            question_uuid=question_uuid,
        )
    ).parsed
