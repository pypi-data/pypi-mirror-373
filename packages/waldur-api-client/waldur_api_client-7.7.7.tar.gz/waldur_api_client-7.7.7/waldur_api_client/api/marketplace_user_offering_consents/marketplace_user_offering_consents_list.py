from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.marketplace_user_offering_consents_list_o_item import MarketplaceUserOfferingConsentsListOItem
from ...models.user_offering_consent import UserOfferingConsent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    has_consent: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    requires_reconsent: Union[Unset, bool] = UNSET,
    user: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["has_consent"] = has_consent

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["offering"] = offering

    json_offering_uuid: Union[Unset, str] = UNSET
    if not isinstance(offering_uuid, Unset):
        json_offering_uuid = str(offering_uuid)
    params["offering_uuid"] = json_offering_uuid

    params["page"] = page

    params["page_size"] = page_size

    params["requires_reconsent"] = requires_reconsent

    params["user"] = user

    json_user_uuid: Union[Unset, str] = UNSET
    if not isinstance(user_uuid, Unset):
        json_user_uuid = str(user_uuid)
    params["user_uuid"] = json_user_uuid

    params["version"] = version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/marketplace-user-offering-consents/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["UserOfferingConsent"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UserOfferingConsent.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["UserOfferingConsent"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    has_consent: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    requires_reconsent: Union[Unset, bool] = UNSET,
    user: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> Response[list["UserOfferingConsent"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        has_consent (Union[Unset, bool]):
        o (Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]]):
        offering (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        requires_reconsent (Union[Unset, bool]):
        user (Union[Unset, str]):
        user_uuid (Union[Unset, UUID]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UserOfferingConsent']]
    """

    kwargs = _get_kwargs(
        has_consent=has_consent,
        o=o,
        offering=offering,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        requires_reconsent=requires_reconsent,
        user=user,
        user_uuid=user_uuid,
        version=version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    has_consent: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    requires_reconsent: Union[Unset, bool] = UNSET,
    user: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> list["UserOfferingConsent"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        has_consent (Union[Unset, bool]):
        o (Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]]):
        offering (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        requires_reconsent (Union[Unset, bool]):
        user (Union[Unset, str]):
        user_uuid (Union[Unset, UUID]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UserOfferingConsent']
    """

    return sync_detailed(
        client=client,
        has_consent=has_consent,
        o=o,
        offering=offering,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        requires_reconsent=requires_reconsent,
        user=user,
        user_uuid=user_uuid,
        version=version,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    has_consent: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    requires_reconsent: Union[Unset, bool] = UNSET,
    user: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> Response[list["UserOfferingConsent"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        has_consent (Union[Unset, bool]):
        o (Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]]):
        offering (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        requires_reconsent (Union[Unset, bool]):
        user (Union[Unset, str]):
        user_uuid (Union[Unset, UUID]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UserOfferingConsent']]
    """

    kwargs = _get_kwargs(
        has_consent=has_consent,
        o=o,
        offering=offering,
        offering_uuid=offering_uuid,
        page=page,
        page_size=page_size,
        requires_reconsent=requires_reconsent,
        user=user,
        user_uuid=user_uuid,
        version=version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    has_consent: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]] = UNSET,
    offering: Union[Unset, str] = UNSET,
    offering_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    requires_reconsent: Union[Unset, bool] = UNSET,
    user: Union[Unset, str] = UNSET,
    user_uuid: Union[Unset, UUID] = UNSET,
    version: Union[Unset, str] = UNSET,
) -> list["UserOfferingConsent"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        has_consent (Union[Unset, bool]):
        o (Union[Unset, list[MarketplaceUserOfferingConsentsListOItem]]):
        offering (Union[Unset, str]):
        offering_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        requires_reconsent (Union[Unset, bool]):
        user (Union[Unset, str]):
        user_uuid (Union[Unset, UUID]):
        version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UserOfferingConsent']
    """

    return (
        await asyncio_detailed(
            client=client,
            has_consent=has_consent,
            o=o,
            offering=offering,
            offering_uuid=offering_uuid,
            page=page,
            page_size=page_size,
            requires_reconsent=requires_reconsent,
            user=user,
            user_uuid=user_uuid,
            version=version,
        )
    ).parsed
