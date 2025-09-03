"""List all tables in the collection"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_tables_list_tables_response_200 import (
    CollectionsTablesListTablesResponse200,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/tables".format(
            collection_id=collection_id,
            version_id=version_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[CollectionsTablesListTablesResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectionsTablesListTablesResponse200.from_dict(response.json())

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
) -> Response[Union[CollectionsTablesListTablesResponse200, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[CollectionsTablesListTablesResponse200, ServerError]]:
    """List all tables in the collection

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsTablesListTablesResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
) -> Union[CollectionsTablesListTablesResponse200]:
    """List all tables in the collection

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsTablesListTablesResponse200]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[CollectionsTablesListTablesResponse200, ServerError]]:
    """List all tables in the collection

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsTablesListTablesResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
) -> Union[CollectionsTablesListTablesResponse200]:
    """List all tables in the collection

    Conformant to GA4GH Data Connect spec as defined in
    https://github.com/ga4gh-discovery/data-
    connect/blob/5956ed13db08a395691808dd30fd17d2c6c5cf35/SPEC.md

    Args:
        collection_id (str):
        version_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsTablesListTablesResponse200]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
