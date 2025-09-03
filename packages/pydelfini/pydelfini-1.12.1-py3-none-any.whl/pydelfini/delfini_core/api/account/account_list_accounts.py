"""List visible accounts"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.account_list import AccountList
from ...models.account_list_accounts_visibility_level import (
    AccountListAccountsVisibilityLevel,
)
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    *,
    author: Union[Unset, bool] = UNSET,
    member: Union[Unset, bool] = UNSET,
    personal: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, AccountListAccountsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["author"] = author

    params["member"] = member

    params["personal"] = personal

    json_visibility_level: Union[Unset, str] = UNSET
    if not isinstance(visibility_level, Unset):
        json_visibility_level = visibility_level.value

    params["visibilityLevel"] = json_visibility_level

    params["meta"] = meta

    params["bmeta"] = bmeta

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/account",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[AccountList, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AccountList.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AccountList, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    author: Union[Unset, bool] = UNSET,
    member: Union[Unset, bool] = UNSET,
    personal: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, AccountListAccountsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Response[Union[AccountList, ServerError]]:
    """List visible accounts

    Args:
        author (Union[Unset, bool]):
        member (Union[Unset, bool]):
        personal (Union[Unset, bool]):
        visibility_level (Union[Unset, AccountListAccountsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AccountList, ServerError]]
    """

    kwargs = _get_kwargs(
        author=author,
        member=member,
        personal=personal,
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
    author: Union[Unset, bool] = UNSET,
    member: Union[Unset, bool] = UNSET,
    personal: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, AccountListAccountsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Union[AccountList]:
    """List visible accounts

    Args:
        author (Union[Unset, bool]):
        member (Union[Unset, bool]):
        personal (Union[Unset, bool]):
        visibility_level (Union[Unset, AccountListAccountsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AccountList]
    """

    response = sync_detailed(
        client=client,
        author=author,
        member=member,
        personal=personal,
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
    author: Union[Unset, bool] = UNSET,
    member: Union[Unset, bool] = UNSET,
    personal: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, AccountListAccountsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Response[Union[AccountList, ServerError]]:
    """List visible accounts

    Args:
        author (Union[Unset, bool]):
        member (Union[Unset, bool]):
        personal (Union[Unset, bool]):
        visibility_level (Union[Unset, AccountListAccountsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AccountList, ServerError]]
    """

    kwargs = _get_kwargs(
        author=author,
        member=member,
        personal=personal,
        visibility_level=visibility_level,
        meta=meta,
        bmeta=bmeta,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    author: Union[Unset, bool] = UNSET,
    member: Union[Unset, bool] = UNSET,
    personal: Union[Unset, bool] = UNSET,
    visibility_level: Union[Unset, AccountListAccountsVisibilityLevel] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Union[AccountList]:
    """List visible accounts

    Args:
        author (Union[Unset, bool]):
        member (Union[Unset, bool]):
        personal (Union[Unset, bool]):
        visibility_level (Union[Unset, AccountListAccountsVisibilityLevel]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AccountList]
    """

    response = await asyncio_detailed(
        client=client,
        author=author,
        member=member,
        personal=personal,
        visibility_level=visibility_level,
        meta=meta,
        bmeta=bmeta,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
