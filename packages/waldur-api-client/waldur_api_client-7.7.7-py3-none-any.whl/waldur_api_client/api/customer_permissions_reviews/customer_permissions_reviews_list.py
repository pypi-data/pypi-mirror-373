from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_permission_review import CustomerPermissionReview
from ...models.customer_permissions_reviews_list_o_item import CustomerPermissionsReviewsListOItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    customer_uuid: Union[Unset, UUID] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[CustomerPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(customer_uuid, Unset):
        json_customer_uuid = str(customer_uuid)
    params["customer_uuid"] = json_customer_uuid

    params["is_pending"] = is_pending

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_reviewer_uuid: Union[Unset, str] = UNSET
    if not isinstance(reviewer_uuid, Unset):
        json_reviewer_uuid = str(reviewer_uuid)
    params["reviewer_uuid"] = json_reviewer_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/customer-permissions-reviews/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> list["CustomerPermissionReview"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CustomerPermissionReview.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CustomerPermissionReview"]]:
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
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[CustomerPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["CustomerPermissionReview"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[CustomerPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CustomerPermissionReview']]
    """

    kwargs = _get_kwargs(
        customer_uuid=customer_uuid,
        is_pending=is_pending,
        o=o,
        page=page,
        page_size=page_size,
        reviewer_uuid=reviewer_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    customer_uuid: Union[Unset, UUID] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[CustomerPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> list["CustomerPermissionReview"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[CustomerPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CustomerPermissionReview']
    """

    return sync_detailed(
        client=client,
        customer_uuid=customer_uuid,
        is_pending=is_pending,
        o=o,
        page=page,
        page_size=page_size,
        reviewer_uuid=reviewer_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    customer_uuid: Union[Unset, UUID] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[CustomerPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> Response[list["CustomerPermissionReview"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[CustomerPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CustomerPermissionReview']]
    """

    kwargs = _get_kwargs(
        customer_uuid=customer_uuid,
        is_pending=is_pending,
        o=o,
        page=page,
        page_size=page_size,
        reviewer_uuid=reviewer_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    customer_uuid: Union[Unset, UUID] = UNSET,
    is_pending: Union[Unset, bool] = UNSET,
    o: Union[Unset, list[CustomerPermissionsReviewsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    reviewer_uuid: Union[Unset, UUID] = UNSET,
) -> list["CustomerPermissionReview"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        customer_uuid (Union[Unset, UUID]):
        is_pending (Union[Unset, bool]):
        o (Union[Unset, list[CustomerPermissionsReviewsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        reviewer_uuid (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CustomerPermissionReview']
    """

    return (
        await asyncio_detailed(
            client=client,
            customer_uuid=customer_uuid,
            is_pending=is_pending,
            o=o,
            page=page,
            page_size=page_size,
            reviewer_uuid=reviewer_uuid,
        )
    ).parsed
