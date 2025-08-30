import datetime
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project import Project
from ...models.projects_list_field_item import ProjectsListFieldItem
from ...models.projects_list_o_item import ProjectsListOItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    backend_id: Union[Unset, str] = UNSET,
    can_admin: Union[Unset, bool] = UNSET,
    can_manage: Union[Unset, bool] = UNSET,
    conceal_finished_projects: Union[Unset, bool] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, list[UUID]] = UNSET,
    customer_abbreviation: Union[Unset, str] = UNSET,
    customer_name: Union[Unset, str] = UNSET,
    customer_native_name: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[ProjectsListFieldItem]] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProjectsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    slug: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["backend_id"] = backend_id

    params["can_admin"] = can_admin

    params["can_manage"] = can_manage

    params["conceal_finished_projects"] = conceal_finished_projects

    json_created: Union[Unset, str] = UNSET
    if not isinstance(created, Unset):
        json_created = created.isoformat()
    params["created"] = json_created

    json_customer: Union[Unset, list[str]] = UNSET
    if not isinstance(customer, Unset):
        json_customer = []
        for customer_item_data in customer:
            customer_item = str(customer_item_data)
            json_customer.append(customer_item)

    params["customer"] = json_customer

    params["customer_abbreviation"] = customer_abbreviation

    params["customer_name"] = customer_name

    params["customer_native_name"] = customer_native_name

    params["description"] = description

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    json_modified: Union[Unset, str] = UNSET
    if not isinstance(modified, Unset):
        json_modified = modified.isoformat()
    params["modified"] = json_modified

    params["name"] = name

    params["name_exact"] = name_exact

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["page"] = page

    params["page_size"] = page_size

    params["query"] = query

    params["slug"] = slug

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/projects/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["Project"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Project.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Project"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    can_admin: Union[Unset, bool] = UNSET,
    can_manage: Union[Unset, bool] = UNSET,
    conceal_finished_projects: Union[Unset, bool] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, list[UUID]] = UNSET,
    customer_abbreviation: Union[Unset, str] = UNSET,
    customer_name: Union[Unset, str] = UNSET,
    customer_native_name: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[ProjectsListFieldItem]] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProjectsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    slug: Union[Unset, str] = UNSET,
) -> Response[list["Project"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        can_admin (Union[Unset, bool]):
        can_manage (Union[Unset, bool]):
        conceal_finished_projects (Union[Unset, bool]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, list[UUID]]):
        customer_abbreviation (Union[Unset, str]):
        customer_name (Union[Unset, str]):
        customer_native_name (Union[Unset, str]):
        description (Union[Unset, str]):
        field (Union[Unset, list[ProjectsListFieldItem]]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[ProjectsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        slug (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Project']]
    """

    kwargs = _get_kwargs(
        backend_id=backend_id,
        can_admin=can_admin,
        can_manage=can_manage,
        conceal_finished_projects=conceal_finished_projects,
        created=created,
        customer=customer,
        customer_abbreviation=customer_abbreviation,
        customer_name=customer_name,
        customer_native_name=customer_native_name,
        description=description,
        field=field,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        page=page,
        page_size=page_size,
        query=query,
        slug=slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    can_admin: Union[Unset, bool] = UNSET,
    can_manage: Union[Unset, bool] = UNSET,
    conceal_finished_projects: Union[Unset, bool] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, list[UUID]] = UNSET,
    customer_abbreviation: Union[Unset, str] = UNSET,
    customer_name: Union[Unset, str] = UNSET,
    customer_native_name: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[ProjectsListFieldItem]] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProjectsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    slug: Union[Unset, str] = UNSET,
) -> list["Project"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        can_admin (Union[Unset, bool]):
        can_manage (Union[Unset, bool]):
        conceal_finished_projects (Union[Unset, bool]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, list[UUID]]):
        customer_abbreviation (Union[Unset, str]):
        customer_name (Union[Unset, str]):
        customer_native_name (Union[Unset, str]):
        description (Union[Unset, str]):
        field (Union[Unset, list[ProjectsListFieldItem]]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[ProjectsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        slug (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Project']
    """

    return sync_detailed(
        client=client,
        backend_id=backend_id,
        can_admin=can_admin,
        can_manage=can_manage,
        conceal_finished_projects=conceal_finished_projects,
        created=created,
        customer=customer,
        customer_abbreviation=customer_abbreviation,
        customer_name=customer_name,
        customer_native_name=customer_native_name,
        description=description,
        field=field,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        page=page,
        page_size=page_size,
        query=query,
        slug=slug,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    can_admin: Union[Unset, bool] = UNSET,
    can_manage: Union[Unset, bool] = UNSET,
    conceal_finished_projects: Union[Unset, bool] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, list[UUID]] = UNSET,
    customer_abbreviation: Union[Unset, str] = UNSET,
    customer_name: Union[Unset, str] = UNSET,
    customer_native_name: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[ProjectsListFieldItem]] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProjectsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    slug: Union[Unset, str] = UNSET,
) -> Response[list["Project"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        can_admin (Union[Unset, bool]):
        can_manage (Union[Unset, bool]):
        conceal_finished_projects (Union[Unset, bool]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, list[UUID]]):
        customer_abbreviation (Union[Unset, str]):
        customer_name (Union[Unset, str]):
        customer_native_name (Union[Unset, str]):
        description (Union[Unset, str]):
        field (Union[Unset, list[ProjectsListFieldItem]]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[ProjectsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        slug (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Project']]
    """

    kwargs = _get_kwargs(
        backend_id=backend_id,
        can_admin=can_admin,
        can_manage=can_manage,
        conceal_finished_projects=conceal_finished_projects,
        created=created,
        customer=customer,
        customer_abbreviation=customer_abbreviation,
        customer_name=customer_name,
        customer_native_name=customer_native_name,
        description=description,
        field=field,
        modified=modified,
        name=name,
        name_exact=name_exact,
        o=o,
        page=page,
        page_size=page_size,
        query=query,
        slug=slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    backend_id: Union[Unset, str] = UNSET,
    can_admin: Union[Unset, bool] = UNSET,
    can_manage: Union[Unset, bool] = UNSET,
    conceal_finished_projects: Union[Unset, bool] = UNSET,
    created: Union[Unset, datetime.datetime] = UNSET,
    customer: Union[Unset, list[UUID]] = UNSET,
    customer_abbreviation: Union[Unset, str] = UNSET,
    customer_name: Union[Unset, str] = UNSET,
    customer_native_name: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    field: Union[Unset, list[ProjectsListFieldItem]] = UNSET,
    modified: Union[Unset, datetime.datetime] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_exact: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProjectsListOItem]] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    query: Union[Unset, str] = UNSET,
    slug: Union[Unset, str] = UNSET,
) -> list["Project"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        backend_id (Union[Unset, str]):
        can_admin (Union[Unset, bool]):
        can_manage (Union[Unset, bool]):
        conceal_finished_projects (Union[Unset, bool]):
        created (Union[Unset, datetime.datetime]):
        customer (Union[Unset, list[UUID]]):
        customer_abbreviation (Union[Unset, str]):
        customer_name (Union[Unset, str]):
        customer_native_name (Union[Unset, str]):
        description (Union[Unset, str]):
        field (Union[Unset, list[ProjectsListFieldItem]]):
        modified (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]):
        name_exact (Union[Unset, str]):
        o (Union[Unset, list[ProjectsListOItem]]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        query (Union[Unset, str]):
        slug (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Project']
    """

    return (
        await asyncio_detailed(
            client=client,
            backend_id=backend_id,
            can_admin=can_admin,
            can_manage=can_manage,
            conceal_finished_projects=conceal_finished_projects,
            created=created,
            customer=customer,
            customer_abbreviation=customer_abbreviation,
            customer_name=customer_name,
            customer_native_name=customer_native_name,
            description=description,
            field=field,
            modified=modified,
            name=name,
            name_exact=name_exact,
            o=o,
            page=page,
            page_size=page_size,
            query=query,
            slug=slug,
        )
    ).parsed
