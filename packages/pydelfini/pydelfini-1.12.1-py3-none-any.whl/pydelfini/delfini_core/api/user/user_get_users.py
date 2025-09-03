"""List users"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.server_error import ServerError
from ...models.user_get_users_response_200 import UserGetUsersResponse200
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    *,
    q: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    id: Union[Unset, List[str]] = UNSET,
    account_id: Union[Unset, List[str]] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["q"] = q

    params["name"] = name

    json_id: Union[Unset, List[str]] = UNSET
    if not isinstance(id, Unset):
        json_id = id

    params["id"] = json_id

    json_account_id: Union[Unset, List[str]] = UNSET
    if not isinstance(account_id, Unset):
        json_account_id = account_id

    params["account_id"] = json_account_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/user",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ServerError, UserGetUsersResponse200]:
    if response.status_code == HTTPStatus.OK:
        response_200 = UserGetUsersResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ServerError, UserGetUsersResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    id: Union[Unset, List[str]] = UNSET,
    account_id: Union[Unset, List[str]] = UNSET,
) -> Response[Union[ServerError, UserGetUsersResponse200]]:
    """List users

    List all users that are visible to the current user.

    Args:
        q (Union[Unset, str]):
        name (Union[Unset, str]):
        id (Union[Unset, List[str]]):
        account_id (Union[Unset, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, UserGetUsersResponse200]]
    """

    kwargs = _get_kwargs(
        q=q,
        name=name,
        id=id,
        account_id=account_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    id: Union[Unset, List[str]] = UNSET,
    account_id: Union[Unset, List[str]] = UNSET,
) -> Union[UserGetUsersResponse200]:
    """List users

    List all users that are visible to the current user.

    Args:
        q (Union[Unset, str]):
        name (Union[Unset, str]):
        id (Union[Unset, List[str]]):
        account_id (Union[Unset, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[UserGetUsersResponse200]
    """

    response = sync_detailed(
        client=client,
        q=q,
        name=name,
        id=id,
        account_id=account_id,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    id: Union[Unset, List[str]] = UNSET,
    account_id: Union[Unset, List[str]] = UNSET,
) -> Response[Union[ServerError, UserGetUsersResponse200]]:
    """List users

    List all users that are visible to the current user.

    Args:
        q (Union[Unset, str]):
        name (Union[Unset, str]):
        id (Union[Unset, List[str]]):
        account_id (Union[Unset, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, UserGetUsersResponse200]]
    """

    kwargs = _get_kwargs(
        q=q,
        name=name,
        id=id,
        account_id=account_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    q: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    id: Union[Unset, List[str]] = UNSET,
    account_id: Union[Unset, List[str]] = UNSET,
) -> Union[UserGetUsersResponse200]:
    """List users

    List all users that are visible to the current user.

    Args:
        q (Union[Unset, str]):
        name (Union[Unset, str]):
        id (Union[Unset, List[str]]):
        account_id (Union[Unset, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[UserGetUsersResponse200]
    """

    response = await asyncio_detailed(
        client=client,
        q=q,
        name=name,
        id=id,
        account_id=account_id,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
