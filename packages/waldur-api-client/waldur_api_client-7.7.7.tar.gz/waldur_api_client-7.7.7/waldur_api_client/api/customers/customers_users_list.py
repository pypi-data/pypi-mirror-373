from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.customer_user import CustomerUser
from ...models.customers_users_list_field_item import CustomersUsersListFieldItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    uuid: UUID,
    *,
    civil_number: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    email: Union[Unset, str] = UNSET,
    field: Union[Unset, list[CustomersUsersListFieldItem]] = UNSET,
    full_name: Union[Unset, str] = UNSET,
    is_active: Union[Unset, str] = UNSET,
    job_title: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_role: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    phone_number: Union[Unset, str] = UNSET,
    project_role: Union[Unset, str] = UNSET,
    registration_method: Union[Unset, str] = UNSET,
    user_keyword: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["civil_number"] = civil_number

    params["description"] = description

    params["email"] = email

    json_field: Union[Unset, list[str]] = UNSET
    if not isinstance(field, Unset):
        json_field = []
        for field_item_data in field:
            field_item = field_item_data.value
            json_field.append(field_item)

    params["field"] = json_field

    params["full_name"] = full_name

    params["is_active"] = is_active

    params["job_title"] = job_title

    params["native_name"] = native_name

    params["o"] = o

    params["organization"] = organization

    params["organization_role"] = organization_role

    params["page"] = page

    params["page_size"] = page_size

    params["phone_number"] = phone_number

    params["project_role"] = project_role

    params["registration_method"] = registration_method

    params["user_keyword"] = user_keyword

    params["username"] = username

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/customers/{uuid}/users/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["CustomerUser"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CustomerUser.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CustomerUser"]]:
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
    civil_number: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    email: Union[Unset, str] = UNSET,
    field: Union[Unset, list[CustomersUsersListFieldItem]] = UNSET,
    full_name: Union[Unset, str] = UNSET,
    is_active: Union[Unset, str] = UNSET,
    job_title: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_role: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    phone_number: Union[Unset, str] = UNSET,
    project_role: Union[Unset, str] = UNSET,
    registration_method: Union[Unset, str] = UNSET,
    user_keyword: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> Response[list["CustomerUser"]]:
    """A list of users connected to the customer.

    Args:
        uuid (UUID):
        civil_number (Union[Unset, str]):
        description (Union[Unset, str]):
        email (Union[Unset, str]):
        field (Union[Unset, list[CustomersUsersListFieldItem]]):
        full_name (Union[Unset, str]):
        is_active (Union[Unset, str]):
        job_title (Union[Unset, str]):
        native_name (Union[Unset, str]):
        o (Union[Unset, str]):
        organization (Union[Unset, str]):
        organization_role (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        phone_number (Union[Unset, str]):
        project_role (Union[Unset, str]):
        registration_method (Union[Unset, str]):
        user_keyword (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CustomerUser']]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        civil_number=civil_number,
        description=description,
        email=email,
        field=field,
        full_name=full_name,
        is_active=is_active,
        job_title=job_title,
        native_name=native_name,
        o=o,
        organization=organization,
        organization_role=organization_role,
        page=page,
        page_size=page_size,
        phone_number=phone_number,
        project_role=project_role,
        registration_method=registration_method,
        user_keyword=user_keyword,
        username=username,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    civil_number: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    email: Union[Unset, str] = UNSET,
    field: Union[Unset, list[CustomersUsersListFieldItem]] = UNSET,
    full_name: Union[Unset, str] = UNSET,
    is_active: Union[Unset, str] = UNSET,
    job_title: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_role: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    phone_number: Union[Unset, str] = UNSET,
    project_role: Union[Unset, str] = UNSET,
    registration_method: Union[Unset, str] = UNSET,
    user_keyword: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> list["CustomerUser"]:
    """A list of users connected to the customer.

    Args:
        uuid (UUID):
        civil_number (Union[Unset, str]):
        description (Union[Unset, str]):
        email (Union[Unset, str]):
        field (Union[Unset, list[CustomersUsersListFieldItem]]):
        full_name (Union[Unset, str]):
        is_active (Union[Unset, str]):
        job_title (Union[Unset, str]):
        native_name (Union[Unset, str]):
        o (Union[Unset, str]):
        organization (Union[Unset, str]):
        organization_role (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        phone_number (Union[Unset, str]):
        project_role (Union[Unset, str]):
        registration_method (Union[Unset, str]):
        user_keyword (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CustomerUser']
    """

    return sync_detailed(
        uuid=uuid,
        client=client,
        civil_number=civil_number,
        description=description,
        email=email,
        field=field,
        full_name=full_name,
        is_active=is_active,
        job_title=job_title,
        native_name=native_name,
        o=o,
        organization=organization,
        organization_role=organization_role,
        page=page,
        page_size=page_size,
        phone_number=phone_number,
        project_role=project_role,
        registration_method=registration_method,
        user_keyword=user_keyword,
        username=username,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    civil_number: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    email: Union[Unset, str] = UNSET,
    field: Union[Unset, list[CustomersUsersListFieldItem]] = UNSET,
    full_name: Union[Unset, str] = UNSET,
    is_active: Union[Unset, str] = UNSET,
    job_title: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_role: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    phone_number: Union[Unset, str] = UNSET,
    project_role: Union[Unset, str] = UNSET,
    registration_method: Union[Unset, str] = UNSET,
    user_keyword: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> Response[list["CustomerUser"]]:
    """A list of users connected to the customer.

    Args:
        uuid (UUID):
        civil_number (Union[Unset, str]):
        description (Union[Unset, str]):
        email (Union[Unset, str]):
        field (Union[Unset, list[CustomersUsersListFieldItem]]):
        full_name (Union[Unset, str]):
        is_active (Union[Unset, str]):
        job_title (Union[Unset, str]):
        native_name (Union[Unset, str]):
        o (Union[Unset, str]):
        organization (Union[Unset, str]):
        organization_role (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        phone_number (Union[Unset, str]):
        project_role (Union[Unset, str]):
        registration_method (Union[Unset, str]):
        user_keyword (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CustomerUser']]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        civil_number=civil_number,
        description=description,
        email=email,
        field=field,
        full_name=full_name,
        is_active=is_active,
        job_title=job_title,
        native_name=native_name,
        o=o,
        organization=organization,
        organization_role=organization_role,
        page=page,
        page_size=page_size,
        phone_number=phone_number,
        project_role=project_role,
        registration_method=registration_method,
        user_keyword=user_keyword,
        username=username,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    civil_number: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    email: Union[Unset, str] = UNSET,
    field: Union[Unset, list[CustomersUsersListFieldItem]] = UNSET,
    full_name: Union[Unset, str] = UNSET,
    is_active: Union[Unset, str] = UNSET,
    job_title: Union[Unset, str] = UNSET,
    native_name: Union[Unset, str] = UNSET,
    o: Union[Unset, str] = UNSET,
    organization: Union[Unset, str] = UNSET,
    organization_role: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    phone_number: Union[Unset, str] = UNSET,
    project_role: Union[Unset, str] = UNSET,
    registration_method: Union[Unset, str] = UNSET,
    user_keyword: Union[Unset, str] = UNSET,
    username: Union[Unset, str] = UNSET,
) -> list["CustomerUser"]:
    """A list of users connected to the customer.

    Args:
        uuid (UUID):
        civil_number (Union[Unset, str]):
        description (Union[Unset, str]):
        email (Union[Unset, str]):
        field (Union[Unset, list[CustomersUsersListFieldItem]]):
        full_name (Union[Unset, str]):
        is_active (Union[Unset, str]):
        job_title (Union[Unset, str]):
        native_name (Union[Unset, str]):
        o (Union[Unset, str]):
        organization (Union[Unset, str]):
        organization_role (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        phone_number (Union[Unset, str]):
        project_role (Union[Unset, str]):
        registration_method (Union[Unset, str]):
        user_keyword (Union[Unset, str]):
        username (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CustomerUser']
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            civil_number=civil_number,
            description=description,
            email=email,
            field=field,
            full_name=full_name,
            is_active=is_active,
            job_title=job_title,
            native_name=native_name,
            o=o,
            organization=organization,
            organization_role=organization_role,
            page=page,
            page_size=page_size,
            phone_number=phone_number,
            project_role=project_role,
            registration_method=registration_method,
            user_keyword=user_keyword,
            username=username,
        )
    ).parsed
