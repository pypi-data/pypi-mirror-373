"""List group members"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.group_members import GroupMembers
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    group_id: str,
    *,
    with_users: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["with_users"] = with_users

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/group/{group_id}/members".format(
            group_id=group_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[GroupMembers, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GroupMembers.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ServerError.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ServerError.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ServerError.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ServerError.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GroupMembers, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_id: str,
    *,
    client: AuthenticatedClient,
    with_users: Union[Unset, bool] = UNSET,
) -> Response[Union[GroupMembers, ServerError]]:
    """List group members

    Args:
        group_id (str):
        with_users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GroupMembers, ServerError]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        with_users=with_users,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group_id: str,
    *,
    client: AuthenticatedClient,
    with_users: Union[Unset, bool] = UNSET,
) -> Union[GroupMembers]:
    """List group members

    Args:
        group_id (str):
        with_users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GroupMembers]
    """

    response = sync_detailed(
        group_id=group_id,
        client=client,
        with_users=with_users,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    group_id: str,
    *,
    client: AuthenticatedClient,
    with_users: Union[Unset, bool] = UNSET,
) -> Response[Union[GroupMembers, ServerError]]:
    """List group members

    Args:
        group_id (str):
        with_users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GroupMembers, ServerError]]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
        with_users=with_users,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_id: str,
    *,
    client: AuthenticatedClient,
    with_users: Union[Unset, bool] = UNSET,
) -> Union[GroupMembers]:
    """List group members

    Args:
        group_id (str):
        with_users (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GroupMembers]
    """

    response = await asyncio_detailed(
        group_id=group_id,
        client=client,
        with_users=with_users,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
