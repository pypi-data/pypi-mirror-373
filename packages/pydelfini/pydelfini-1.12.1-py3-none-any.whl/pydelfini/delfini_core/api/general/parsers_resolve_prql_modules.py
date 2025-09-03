"""Resolve PRQL modules"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.parsers_resolve_prql_modules_response_200 import (
    ParsersResolvePrqlModulesResponse200,
)
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET


def _get_kwargs(
    *,
    href: List[str],
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_href = href

    params["href"] = json_href

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/parsers/prql/modules",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ParsersResolvePrqlModulesResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ParsersResolvePrqlModulesResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ParsersResolvePrqlModulesResponse200, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    href: List[str],
) -> Response[Union[ParsersResolvePrqlModulesResponse200, ServerError]]:
    """Resolve PRQL modules

    Fetch the PRQL module(s) content given the href path in the
    PRQL module reference

    Args:
        href (List[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ParsersResolvePrqlModulesResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        href=href,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    href: List[str],
) -> Union[ParsersResolvePrqlModulesResponse200]:
    """Resolve PRQL modules

    Fetch the PRQL module(s) content given the href path in the
    PRQL module reference

    Args:
        href (List[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ParsersResolvePrqlModulesResponse200]
    """

    response = sync_detailed(
        client=client,
        href=href,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    href: List[str],
) -> Response[Union[ParsersResolvePrqlModulesResponse200, ServerError]]:
    """Resolve PRQL modules

    Fetch the PRQL module(s) content given the href path in the
    PRQL module reference

    Args:
        href (List[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ParsersResolvePrqlModulesResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        href=href,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    href: List[str],
) -> Union[ParsersResolvePrqlModulesResponse200]:
    """Resolve PRQL modules

    Fetch the PRQL module(s) content given the href path in the
    PRQL module reference

    Args:
        href (List[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ParsersResolvePrqlModulesResponse200]
    """

    response = await asyncio_detailed(
        client=client,
        href=href,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
