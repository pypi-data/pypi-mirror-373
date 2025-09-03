"""List groups"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.group_get_groups_response_200 import GroupGetGroupsResponse200
from ...models.group_get_groups_visibility_level import GroupGetGroupsVisibilityLevel
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    *,
    member: Union[Unset, bool] = UNSET,
    admin: Union[Unset, bool] = UNSET,
    controlled: Union[Unset, bool] = UNSET,
    account_linked: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, GroupGetGroupsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["member"] = member

    params["admin"] = admin

    params["controlled"] = controlled

    params["accountLinked"] = account_linked

    json_visibility_level: Union[Unset, str] = UNSET
    if not isinstance(visibility_level, Unset):
        json_visibility_level = visibility_level.value

    params["visibilityLevel"] = json_visibility_level

    params["meta"] = meta

    params["bmeta"] = bmeta

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/group",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[GroupGetGroupsResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GroupGetGroupsResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GroupGetGroupsResponse200, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    member: Union[Unset, bool] = UNSET,
    admin: Union[Unset, bool] = UNSET,
    controlled: Union[Unset, bool] = UNSET,
    account_linked: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, GroupGetGroupsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Response[Union[GroupGetGroupsResponse200, ServerError]]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        member (Union[Unset, bool]):
        admin (Union[Unset, bool]):
        controlled (Union[Unset, bool]):
        account_linked (Union[Unset, bool]):
        visibility_level (Union[Unset, GroupGetGroupsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GroupGetGroupsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        member=member,
        admin=admin,
        controlled=controlled,
        account_linked=account_linked,
        visibility_level=visibility_level,
        meta=meta,
        bmeta=bmeta,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    member: Union[Unset, bool] = UNSET,
    admin: Union[Unset, bool] = UNSET,
    controlled: Union[Unset, bool] = UNSET,
    account_linked: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, GroupGetGroupsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Union[GroupGetGroupsResponse200]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        member (Union[Unset, bool]):
        admin (Union[Unset, bool]):
        controlled (Union[Unset, bool]):
        account_linked (Union[Unset, bool]):
        visibility_level (Union[Unset, GroupGetGroupsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GroupGetGroupsResponse200]
    """

    response = sync_detailed(
        client=client,
        member=member,
        admin=admin,
        controlled=controlled,
        account_linked=account_linked,
        visibility_level=visibility_level,
        meta=meta,
        bmeta=bmeta,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    member: Union[Unset, bool] = UNSET,
    admin: Union[Unset, bool] = UNSET,
    controlled: Union[Unset, bool] = UNSET,
    account_linked: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, GroupGetGroupsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Response[Union[GroupGetGroupsResponse200, ServerError]]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        member (Union[Unset, bool]):
        admin (Union[Unset, bool]):
        controlled (Union[Unset, bool]):
        account_linked (Union[Unset, bool]):
        visibility_level (Union[Unset, GroupGetGroupsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GroupGetGroupsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        member=member,
        admin=admin,
        controlled=controlled,
        account_linked=account_linked,
        visibility_level=visibility_level,
        meta=meta,
        bmeta=bmeta,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    member: Union[Unset, bool] = UNSET,
    admin: Union[Unset, bool] = UNSET,
    controlled: Union[Unset, bool] = UNSET,
    account_linked: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, GroupGetGroupsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Union[GroupGetGroupsResponse200]:
    """List groups

    List all the groups that are visible to the current user,
    whether logged in or not.

    Args:
        member (Union[Unset, bool]):
        admin (Union[Unset, bool]):
        controlled (Union[Unset, bool]):
        account_linked (Union[Unset, bool]):
        visibility_level (Union[Unset, GroupGetGroupsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GroupGetGroupsResponse200]
    """

    response = await asyncio_detailed(
        client=client,
        member=member,
        admin=admin,
        controlled=controlled,
        account_linked=account_linked,
        visibility_level=visibility_level,
        meta=meta,
        bmeta=bmeta,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
