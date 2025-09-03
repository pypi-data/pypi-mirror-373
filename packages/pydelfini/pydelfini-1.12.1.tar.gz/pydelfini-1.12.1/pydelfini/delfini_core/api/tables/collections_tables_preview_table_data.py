"""Preview changes to a table's definition"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_tables_preview_table_data_body import (
    CollectionsTablesPreviewTableDataBody,
)
from ...models.server_error import ServerError
from ...models.table_data import TableData
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    table_name: str,
    *,
    body: CollectionsTablesPreviewTableDataBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/{version_id}/tables/{table_name}/preview".format(
            collection_id=collection_id,
            version_id=version_id,
            table_name=table_name,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ServerError, TableData]:
    if response.status_code == HTTPStatus.OK:
        response_200 = TableData.from_dict(response.json())

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
) -> Response[Union[ServerError, TableData]]:
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
    body: CollectionsTablesPreviewTableDataBody,
) -> Response[Union[ServerError, TableData]]:
    """Preview changes to a table's definition

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        body (CollectionsTablesPreviewTableDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, TableData]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        body=body,
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
    body: CollectionsTablesPreviewTableDataBody,
) -> Union[TableData]:
    """Preview changes to a table's definition

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        body (CollectionsTablesPreviewTableDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[TableData]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        client=client,
        body=body,
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
    body: CollectionsTablesPreviewTableDataBody,
) -> Response[Union[ServerError, TableData]]:
    """Preview changes to a table's definition

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        body (CollectionsTablesPreviewTableDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, TableData]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    table_name: str,
    *,
    client: AuthenticatedClient,
    body: CollectionsTablesPreviewTableDataBody,
) -> Union[TableData]:
    """Preview changes to a table's definition

    Args:
        collection_id (str):
        version_id (str):
        table_name (str):
        body (CollectionsTablesPreviewTableDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[TableData]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        table_name=table_name,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
