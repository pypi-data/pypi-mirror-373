"""Search a data dictionary for data elements compatible with an item's columns
"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.search_dictionaries_by_item_response import (
    SearchDictionariesByItemResponse,
)
from ...models.search_search_dictionaries_by_item_body import (
    SearchSearchDictionariesByItemBody,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    *,
    body: SearchSearchDictionariesByItemBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/search/dictionaries/byitem",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[SearchDictionariesByItemResponse, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SearchDictionariesByItemResponse.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ServerError.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
        response_415 = ServerError.from_dict(response.json())

        return response_415
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[SearchDictionariesByItemResponse, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SearchSearchDictionariesByItemBody,
) -> Response[Union[SearchDictionariesByItemResponse, ServerError]]:
    """Search a data dictionary for data elements compatible with an item's columns

    This performs a 'forward search' for data elements from the
    provided source that are likely to describe columns in the
    provided item. The results are returned on a per-column basis,
    paginated across the columns in the provided item.

    The current method uses column names as full-text search
    queries against the text extracted from the data element
    definition, including its title, descriptions, and concept
    codes.

    Args:
        body (SearchSearchDictionariesByItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SearchDictionariesByItemResponse, ServerError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: SearchSearchDictionariesByItemBody,
) -> Union[SearchDictionariesByItemResponse]:
    """Search a data dictionary for data elements compatible with an item's columns

    This performs a 'forward search' for data elements from the
    provided source that are likely to describe columns in the
    provided item. The results are returned on a per-column basis,
    paginated across the columns in the provided item.

    The current method uses column names as full-text search
    queries against the text extracted from the data element
    definition, including its title, descriptions, and concept
    codes.

    Args:
        body (SearchSearchDictionariesByItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SearchDictionariesByItemResponse]
    """

    response = sync_detailed(
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SearchSearchDictionariesByItemBody,
) -> Response[Union[SearchDictionariesByItemResponse, ServerError]]:
    """Search a data dictionary for data elements compatible with an item's columns

    This performs a 'forward search' for data elements from the
    provided source that are likely to describe columns in the
    provided item. The results are returned on a per-column basis,
    paginated across the columns in the provided item.

    The current method uses column names as full-text search
    queries against the text extracted from the data element
    definition, including its title, descriptions, and concept
    codes.

    Args:
        body (SearchSearchDictionariesByItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SearchDictionariesByItemResponse, ServerError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SearchSearchDictionariesByItemBody,
) -> Union[SearchDictionariesByItemResponse]:
    """Search a data dictionary for data elements compatible with an item's columns

    This performs a 'forward search' for data elements from the
    provided source that are likely to describe columns in the
    provided item. The results are returned on a per-column basis,
    paginated across the columns in the provided item.

    The current method uses column names as full-text search
    queries against the text extracted from the data element
    definition, including its title, descriptions, and concept
    codes.

    Args:
        body (SearchSearchDictionariesByItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SearchDictionariesByItemResponse]
    """

    response = await asyncio_detailed(
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
