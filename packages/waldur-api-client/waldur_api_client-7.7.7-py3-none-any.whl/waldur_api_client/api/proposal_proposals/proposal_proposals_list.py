from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.proposal import Proposal
from ...models.proposal_proposals_list_o_item import ProposalProposalsListOItem
from ...models.proposal_proposals_list_state_item import ProposalProposalsListStateItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    call_uuid: Union[Unset, UUID] = UNSET,
    name: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProposalProposalsListOItem]] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    round_: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[ProposalProposalsListStateItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_call_uuid: Union[Unset, str] = UNSET
    if not isinstance(call_uuid, Unset):
        json_call_uuid = str(call_uuid)
    params["call_uuid"] = json_call_uuid

    params["name"] = name

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    json_organization_uuid: Union[Unset, str] = UNSET
    if not isinstance(organization_uuid, Unset):
        json_organization_uuid = str(organization_uuid)
    params["organization_uuid"] = json_organization_uuid

    params["page"] = page

    params["page_size"] = page_size

    json_round_: Union[Unset, str] = UNSET
    if not isinstance(round_, Unset):
        json_round_ = str(round_)
    params["round"] = json_round_

    json_state: Union[Unset, list[str]] = UNSET
    if not isinstance(state, Unset):
        json_state = []
        for state_item_data in state:
            state_item = state_item_data.value
            json_state.append(state_item)

    params["state"] = json_state

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/proposal-proposals/",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> list["Proposal"]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Proposal.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Proposal"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    call_uuid: Union[Unset, UUID] = UNSET,
    name: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProposalProposalsListOItem]] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    round_: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[ProposalProposalsListStateItem]] = UNSET,
) -> Response[list["Proposal"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        call_uuid (Union[Unset, UUID]):
        name (Union[Unset, str]):
        o (Union[Unset, list[ProposalProposalsListOItem]]):
        organization_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        round_ (Union[Unset, UUID]):
        state (Union[Unset, list[ProposalProposalsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Proposal']]
    """

    kwargs = _get_kwargs(
        call_uuid=call_uuid,
        name=name,
        o=o,
        organization_uuid=organization_uuid,
        page=page,
        page_size=page_size,
        round_=round_,
        state=state,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    call_uuid: Union[Unset, UUID] = UNSET,
    name: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProposalProposalsListOItem]] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    round_: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[ProposalProposalsListStateItem]] = UNSET,
) -> list["Proposal"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        call_uuid (Union[Unset, UUID]):
        name (Union[Unset, str]):
        o (Union[Unset, list[ProposalProposalsListOItem]]):
        organization_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        round_ (Union[Unset, UUID]):
        state (Union[Unset, list[ProposalProposalsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Proposal']
    """

    return sync_detailed(
        client=client,
        call_uuid=call_uuid,
        name=name,
        o=o,
        organization_uuid=organization_uuid,
        page=page,
        page_size=page_size,
        round_=round_,
        state=state,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    call_uuid: Union[Unset, UUID] = UNSET,
    name: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProposalProposalsListOItem]] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    round_: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[ProposalProposalsListStateItem]] = UNSET,
) -> Response[list["Proposal"]]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        call_uuid (Union[Unset, UUID]):
        name (Union[Unset, str]):
        o (Union[Unset, list[ProposalProposalsListOItem]]):
        organization_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        round_ (Union[Unset, UUID]):
        state (Union[Unset, list[ProposalProposalsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Proposal']]
    """

    kwargs = _get_kwargs(
        call_uuid=call_uuid,
        name=name,
        o=o,
        organization_uuid=organization_uuid,
        page=page,
        page_size=page_size,
        round_=round_,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    call_uuid: Union[Unset, UUID] = UNSET,
    name: Union[Unset, str] = UNSET,
    o: Union[Unset, list[ProposalProposalsListOItem]] = UNSET,
    organization_uuid: Union[Unset, UUID] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    round_: Union[Unset, UUID] = UNSET,
    state: Union[Unset, list[ProposalProposalsListStateItem]] = UNSET,
) -> list["Proposal"]:
    """Mixin to optimize HEAD requests for DRF views bypassing serializer processing

    Args:
        call_uuid (Union[Unset, UUID]):
        name (Union[Unset, str]):
        o (Union[Unset, list[ProposalProposalsListOItem]]):
        organization_uuid (Union[Unset, UUID]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        round_ (Union[Unset, UUID]):
        state (Union[Unset, list[ProposalProposalsListStateItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Proposal']
    """

    return (
        await asyncio_detailed(
            client=client,
            call_uuid=call_uuid,
            name=name,
            o=o,
            organization_uuid=organization_uuid,
            page=page,
            page_size=page_size,
            round_=round_,
            state=state,
        )
    ).parsed
