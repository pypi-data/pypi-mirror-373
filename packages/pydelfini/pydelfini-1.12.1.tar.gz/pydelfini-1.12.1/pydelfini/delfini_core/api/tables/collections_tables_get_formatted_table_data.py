"""Get the contents of a data table in specified format"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_tables_get_formatted_table_data_export_format import (
    CollectionsTablesGetFormattedTableDataExportFormat,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    table_name: str,
    export_format: CollectionsTablesGetFormattedTableDataExportFormat,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/tables/{table_name}/format/{export_format}".format(
            collection_id=collection_id,
            version_id=version_id,
            table_name=table_name,
            export_format=export_format,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ServerError, str]:
    if response.status_code == HTTPStatus.OK:
        response_200 = response.text
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
) -> Response[Union[ServerError, str]]:
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
    export_format: CollectionsTablesGetFormattedTableDataExportFormat,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, str]]:
    """Get the contents of a data table in specified format

    Get the contents of a data table in specified format: csv, tsv, parquet or excel

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        export_format (CollectionsTablesGetFormattedTableDataExportFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, str]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        export_format=export_format,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    version_id: str,
    table_name: str,
    export_format: CollectionsTablesGetFormattedTableDataExportFormat,
    *,
    client: AuthenticatedClient,
) -> Union[str]:
    """Get the contents of a data table in specified format

    Get the contents of a data table in specified format: csv, tsv, parquet or excel

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        export_format (CollectionsTablesGetFormattedTableDataExportFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[str]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        export_format=export_format,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    table_name: str,
    export_format: CollectionsTablesGetFormattedTableDataExportFormat,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, str]]:
    """Get the contents of a data table in specified format

    Get the contents of a data table in specified format: csv, tsv, parquet or excel

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        export_format (CollectionsTablesGetFormattedTableDataExportFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, str]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        export_format=export_format,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    table_name: str,
    export_format: CollectionsTablesGetFormattedTableDataExportFormat,
    *,
    client: AuthenticatedClient,
) -> Union[str]:
    """Get the contents of a data table in specified format

    Get the contents of a data table in specified format: csv, tsv, parquet or excel

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        export_format (CollectionsTablesGetFormattedTableDataExportFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[str]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        export_format=export_format,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
