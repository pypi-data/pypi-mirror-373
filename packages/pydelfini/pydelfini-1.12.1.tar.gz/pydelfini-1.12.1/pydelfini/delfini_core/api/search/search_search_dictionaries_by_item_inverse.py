"""Given a data dictionary, identify candidate item columns that
align and validate
"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.search_dictionaries_by_item_inverse_response import (
    SearchDictionariesByItemInverseResponse,
)
from ...models.search_search_dictionaries_by_item_inverse_body import (
    SearchSearchDictionariesByItemInverseBody,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    *,
    body: SearchSearchDictionariesByItemInverseBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/search/dictionaries/byiteminverse",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[SearchDictionariesByItemInverseResponse, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SearchDictionariesByItemInverseResponse.from_dict(
            response.json()
        )

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
) -> Response[Union[SearchDictionariesByItemInverseResponse, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SearchSearchDictionariesByItemInverseBody,
) -> Response[Union[SearchDictionariesByItemInverseResponse, ServerError]]:
    """Given a data dictionary, identify candidate item columns that
    align and validate

    This performs a 'reverse search' for columns in the provided
    item that are likely to align with data elements in the
    provided source. The results are returned per data element,
    without pagination currently.

    The current method uses the same approach as the 'forward
    search', performing full-text search queries using the column
    names against the data element definitions. These hits are
    then collated by data element and ranked to provide the most
    likely column hits for each data element.

    Args:
        body (SearchSearchDictionariesByItemInverseBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SearchDictionariesByItemInverseResponse, ServerError]]
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
    body: SearchSearchDictionariesByItemInverseBody,
) -> Union[SearchDictionariesByItemInverseResponse]:
    """Given a data dictionary, identify candidate item columns that
    align and validate

    This performs a 'reverse search' for columns in the provided
    item that are likely to align with data elements in the
    provided source. The results are returned per data element,
    without pagination currently.

    The current method uses the same approach as the 'forward
    search', performing full-text search queries using the column
    names against the data element definitions. These hits are
    then collated by data element and ranked to provide the most
    likely column hits for each data element.

    Args:
        body (SearchSearchDictionariesByItemInverseBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SearchDictionariesByItemInverseResponse]
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
    body: SearchSearchDictionariesByItemInverseBody,
) -> Response[Union[SearchDictionariesByItemInverseResponse, ServerError]]:
    """Given a data dictionary, identify candidate item columns that
    align and validate

    This performs a 'reverse search' for columns in the provided
    item that are likely to align with data elements in the
    provided source. The results are returned per data element,
    without pagination currently.

    The current method uses the same approach as the 'forward
    search', performing full-text search queries using the column
    names against the data element definitions. These hits are
    then collated by data element and ranked to provide the most
    likely column hits for each data element.

    Args:
        body (SearchSearchDictionariesByItemInverseBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SearchDictionariesByItemInverseResponse, ServerError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SearchSearchDictionariesByItemInverseBody,
) -> Union[SearchDictionariesByItemInverseResponse]:
    """Given a data dictionary, identify candidate item columns that
    align and validate

    This performs a 'reverse search' for columns in the provided
    item that are likely to align with data elements in the
    provided source. The results are returned per data element,
    without pagination currently.

    The current method uses the same approach as the 'forward
    search', performing full-text search queries using the column
    names against the data element definitions. These hits are
    then collated by data element and ranked to provide the most
    likely column hits for each data element.

    Args:
        body (SearchSearchDictionariesByItemInverseBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SearchDictionariesByItemInverseResponse]
    """

    response = await asyncio_detailed(
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
