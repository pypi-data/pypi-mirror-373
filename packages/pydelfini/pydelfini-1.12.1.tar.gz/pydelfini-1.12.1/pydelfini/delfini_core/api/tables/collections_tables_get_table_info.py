"""Get information on a specific table"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.server_error import ServerError
from ...models.table import Table
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    table_name: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/tables/{table_name}/info".format(
            collection_id=collection_id,
            version_id=version_id,
            table_name=table_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ServerError, Table]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Table.from_dict(response.json())

        return response_200
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
) -> Response[Union[ServerError, Table]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    version_id: str,
    table_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, Table]]:
    """Get information on a specific table

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, Table]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    version_id: str,
    table_name: str,
    *,
    client: AuthenticatedClient,
) -> Union[Table]:
    """Get information on a specific table

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Table]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    table_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, Table]]:
    """Get information on a specific table

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, Table]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    table_name: str,
    *,
    client: AuthenticatedClient,
) -> Union[Table]:
    """Get information on a specific table

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Table]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
