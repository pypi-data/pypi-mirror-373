from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.user_agreement import UserAgreement
from ...models.user_agreements_list_agreement_type import UserAgreementsListAgreementType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    agreement_type: Union[Unset, UserAgreementsListAgreementType] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_agreement_type: Union[Unset, str] = UNSET
    if not isinstance(agreement_type, Unset):
        json_agreement_type = agreement_type.value

    params["agreement_type"] = json_agreement_type

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/user-agreements/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["UserAgreement"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UserAgreement.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["UserAgreement"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    agreement_type: Union[Unset, UserAgreementsListAgreementType] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[list["UserAgreement"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        agreement_type (Union[Unset, UserAgreementsListAgreementType]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UserAgreement']]
    """

    kwargs = _get_kwargs(
        agreement_type=agreement_type,
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
    agreement_type: Union[Unset, UserAgreementsListAgreementType] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> list["UserAgreement"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        agreement_type (Union[Unset, UserAgreementsListAgreementType]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UserAgreement']
    """

    return sync_detailed(
        client=client,
        agreement_type=agreement_type,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    agreement_type: Union[Unset, UserAgreementsListAgreementType] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> Response[list["UserAgreement"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        agreement_type (Union[Unset, UserAgreementsListAgreementType]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UserAgreement']]
    """

    kwargs = _get_kwargs(
        agreement_type=agreement_type,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    agreement_type: Union[Unset, UserAgreementsListAgreementType] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
) -> list["UserAgreement"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        agreement_type (Union[Unset, UserAgreementsListAgreementType]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UserAgreement']
    """

    return (
        await asyncio_detailed(
            client=client,
            agreement_type=agreement_type,
            page=page,
            page_size=page_size,
        )
    ).parsed
