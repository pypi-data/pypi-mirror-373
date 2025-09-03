"""Get a page from this account"""
from http import HTTPStatus
from io import BytesIO
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.server_error import ServerError
from ...types import File
from ...types import Response


def _get_kwargs(
    account_id: str,
    page_path: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/account/{account_id}/pages/{page_path}".format(
            account_id=account_id,
            page_path=page_path,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[File, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = File(payload=BytesIO(response.content))

        return response_200
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
) -> Response[Union[File, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    page_path: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[File, ServerError]]:
    """Get a page from this account

    Args:
        account_id (str):
        page_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[File, ServerError]]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page_path=page_path,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    page_path: str,
    *,
    client: AuthenticatedClient,
) -> Union[File]:
    """Get a page from this account

    Args:
        account_id (str):
        page_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[File]
    """

    response = sync_detailed(
        account_id=account_id,
        page_path=page_path,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    account_id: str,
    page_path: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[File, ServerError]]:
    """Get a page from this account

    Args:
        account_id (str):
        page_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[File, ServerError]]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page_path=page_path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    page_path: str,
    *,
    client: AuthenticatedClient,
) -> Union[File]:
    """Get a page from this account

    Args:
        account_id (str):
        page_path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[File]
    """

    response = await asyncio_detailed(
        account_id=account_id,
        page_path=page_path,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
