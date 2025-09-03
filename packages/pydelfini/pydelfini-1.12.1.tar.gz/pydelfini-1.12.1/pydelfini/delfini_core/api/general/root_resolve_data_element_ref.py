"""Resolve Data Element URL"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.data_element import DataElement
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    *,
    url_query: str,
    collection_id: Union[Unset, str] = UNSET,
    version_id: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["url"] = url_query

    params["collection_id"] = collection_id

    params["version_id"] = version_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/resolve",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[DataElement, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = DataElement.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ServerError.from_dict(response.json())

        return response_400
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
) -> Response[Union[DataElement, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    url_query: str,
    collection_id: Union[Unset, str] = UNSET,
    version_id: Union[Unset, str] = UNSET,
) -> Response[Union[DataElement, ServerError]]:
    """Resolve Data Element URL

    Retrieve a data element from a data element URL

    Args:
        url_query (str):
        collection_id (Union[Unset, str]):
        version_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DataElement, ServerError]]
    """

    kwargs = _get_kwargs(
        url_query=url_query,
        collection_id=collection_id,
        version_id=version_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    url_query: str,
    collection_id: Union[Unset, str] = UNSET,
    version_id: Union[Unset, str] = UNSET,
) -> Union[DataElement]:
    """Resolve Data Element URL

    Retrieve a data element from a data element URL

    Args:
        url_query (str):
        collection_id (Union[Unset, str]):
        version_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DataElement]
    """

    response = sync_detailed(
        client=client,
        url_query=url_query,
        collection_id=collection_id,
        version_id=version_id,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    url_query: str,
    collection_id: Union[Unset, str] = UNSET,
    version_id: Union[Unset, str] = UNSET,
) -> Response[Union[DataElement, ServerError]]:
    """Resolve Data Element URL

    Retrieve a data element from a data element URL

    Args:
        url_query (str):
        collection_id (Union[Unset, str]):
        version_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DataElement, ServerError]]
    """

    kwargs = _get_kwargs(
        url_query=url_query,
        collection_id=collection_id,
        version_id=version_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    url_query: str,
    collection_id: Union[Unset, str] = UNSET,
    version_id: Union[Unset, str] = UNSET,
) -> Union[DataElement]:
    """Resolve Data Element URL

    Retrieve a data element from a data element URL

    Args:
        url_query (str):
        collection_id (Union[Unset, str]):
        version_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DataElement]
    """

    response = await asyncio_detailed(
        client=client,
        url_query=url_query,
        collection_id=collection_id,
        version_id=version_id,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
