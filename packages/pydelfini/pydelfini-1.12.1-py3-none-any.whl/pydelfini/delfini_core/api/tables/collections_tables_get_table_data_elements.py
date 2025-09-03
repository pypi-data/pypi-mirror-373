"""Resolve and return all data elements on a tabular data item"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_tables_get_table_data_elements_response_200 import (
    CollectionsTablesGetTableDataElementsResponse200,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    table_name: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/tables/{table_name}/elements".format(
            collection_id=collection_id,
            version_id=version_id,
            table_name=table_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[CollectionsTablesGetTableDataElementsResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectionsTablesGetTableDataElementsResponse200.from_dict(
            response.json()
        )

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
    if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
        response_415 = ServerError.from_dict(response.json())

        return response_415
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CollectionsTablesGetTableDataElementsResponse200, ServerError]]:
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
) -> Response[Union[CollectionsTablesGetTableDataElementsResponse200, ServerError]]:
    """Resolve and return all data elements on a tabular data item

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsTablesGetTableDataElementsResponse200, ServerError]]
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
) -> Union[CollectionsTablesGetTableDataElementsResponse200]:
    """Resolve and return all data elements on a tabular data item

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsTablesGetTableDataElementsResponse200]
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
) -> Response[Union[CollectionsTablesGetTableDataElementsResponse200, ServerError]]:
    """Resolve and return all data elements on a tabular data item

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsTablesGetTableDataElementsResponse200, ServerError]]
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
) -> Union[CollectionsTablesGetTableDataElementsResponse200]:
    """Resolve and return all data elements on a tabular data item

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsTablesGetTableDataElementsResponse200]
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
