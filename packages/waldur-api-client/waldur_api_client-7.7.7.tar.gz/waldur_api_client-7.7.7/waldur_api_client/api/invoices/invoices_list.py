import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.invoice import Invoice
from ...models.invoices_list_field_item import InvoicesListFieldItem
from ...models.invoices_list_o_item import InvoicesListOItem
from ...models.invoices_list_state_item import InvoicesListStateItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    created: Union[Unset, datetime.date] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[InvoicesListFieldItem]] = UNSET,
    month: Union[Unset, int] = UNSET,
    o: Union[Unset, list[InvoicesListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[InvoicesListStateItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_created: Union[Unset, str] = UNSET
    if not isinstance(created, Unset):
        json_created = created.isoformat()
    params["created"] = json_created

    params["customer"] = customer

    json_customer_uuid: Union[Unset, str] = UNSET
    if not isinstance(customer_uuid, Unset):
        json_customer_uuid = str(customer_uuid)
    params["customer_uuid"] = json_customer_uuid

    json_end_date: Union[Unset, str] = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["end_date"] = json_end_date

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["month"] = month

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    json_start_date: Union[Unset, str] = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["start_date"] = json_start_date

    json_state: Union[Unset, list[str]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    params["year"] = year

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/invoices/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["Invoice"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Invoice.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Invoice"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    created: Union[Unset, datetime.date] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[InvoicesListFieldItem]] = UNSET,
    month: Union[Unset, int] = UNSET,
    o: Union[Unset, list[InvoicesListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[InvoicesListStateItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
) -> Response[list["Invoice"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created (Union[Unset, datetime.date]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        end_date (Union[Unset, datetime.date]):
        field (Union[Unset, list[InvoicesListFieldItem]]):
        month (Union[Unset, int]):
        o (Union[Unset, list[InvoicesListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        start_date (Union[Unset, datetime.date]):
        state (Union[Unset, list[InvoicesListStateItem]]):
        year (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Invoice']]
    """

    kwargs = _get_kwargs(
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        end_date=end_date,
        field=field,
        month=month,
        o=o,
        page=page,
        page_size=page_size,
        start_date=start_date,
        state=state,
        year=year,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    created: Union[Unset, datetime.date] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[InvoicesListFieldItem]] = UNSET,
    month: Union[Unset, int] = UNSET,
    o: Union[Unset, list[InvoicesListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[InvoicesListStateItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
) -> list["Invoice"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created (Union[Unset, datetime.date]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        end_date (Union[Unset, datetime.date]):
        field (Union[Unset, list[InvoicesListFieldItem]]):
        month (Union[Unset, int]):
        o (Union[Unset, list[InvoicesListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        start_date (Union[Unset, datetime.date]):
        state (Union[Unset, list[InvoicesListStateItem]]):
        year (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Invoice']
    """

    return sync_detailed(
        client=client,
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        end_date=end_date,
        field=field,
        month=month,
        o=o,
        page=page,
        page_size=page_size,
        start_date=start_date,
        state=state,
        year=year,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    created: Union[Unset, datetime.date] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[InvoicesListFieldItem]] = UNSET,
    month: Union[Unset, int] = UNSET,
    o: Union[Unset, list[InvoicesListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[InvoicesListStateItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
) -> Response[list["Invoice"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created (Union[Unset, datetime.date]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        end_date (Union[Unset, datetime.date]):
        field (Union[Unset, list[InvoicesListFieldItem]]):
        month (Union[Unset, int]):
        o (Union[Unset, list[InvoicesListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        start_date (Union[Unset, datetime.date]):
        state (Union[Unset, list[InvoicesListStateItem]]):
        year (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Invoice']]
    """

    kwargs = _get_kwargs(
        created=created,
        customer=customer,
        customer_uuid=customer_uuid,
        end_date=end_date,
        field=field,
        month=month,
        o=o,
        page=page,
        page_size=page_size,
        start_date=start_date,
        state=state,
        year=year,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    created: Union[Unset, datetime.date] = UNSET,
    customer: Union[Unset, str] = UNSET,
    customer_uuid: Union[Unset, UUID] = UNSET,
    end_date: Union[Unset, datetime.date] = UNSET,
    field: Union[Unset, list[InvoicesListFieldItem]] = UNSET,
    month: Union[Unset, int] = UNSET,
    o: Union[Unset, list[InvoicesListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    start_date: Union[Unset, datetime.date] = UNSET,
    state: Union[Unset, list[InvoicesListStateItem]] = UNSET,
    year: Union[Unset, int] = UNSET,
) -> list["Invoice"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        created (Union[Unset, datetime.date]):
        customer (Union[Unset, str]):
        customer_uuid (Union[Unset, UUID]):
        end_date (Union[Unset, datetime.date]):
        field (Union[Unset, list[InvoicesListFieldItem]]):
        month (Union[Unset, int]):
        o (Union[Unset, list[InvoicesListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        start_date (Union[Unset, datetime.date]):
        state (Union[Unset, list[InvoicesListStateItem]]):
        year (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Invoice']
    """

    return (
        await asyncio_detailed(
            client=client,
            created=created,
            customer=customer,
            customer_uuid=customer_uuid,
            end_date=end_date,
            field=field,
            month=month,
            o=o,
            page=page,
            page_size=page_size,
            start_date=start_date,
            state=state,
            year=year,
        )
    ).parsed
