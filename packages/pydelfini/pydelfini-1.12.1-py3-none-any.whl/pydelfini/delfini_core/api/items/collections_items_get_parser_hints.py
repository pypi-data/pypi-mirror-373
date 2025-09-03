"""Get hints for the proposed parser of an item"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.item_parser import ItemParser
from ...models.parser import Parser
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    body: Union["ItemParser", None],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/{version_id}/items/{item_id}/parserHints".format(
            collection_id=collection_id,
            version_id=version_id,
            item_id=item_id,
        ),
    }

    _body: Union[Dict[str, Any], None]
    if isinstance(body, ItemParser):
        _body = body.to_dict()
    else:
        _body = body

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Parser, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Parser.from_dict(response.json())

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
) -> Response[Union[Parser, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["ItemParser", None],
) -> Response[Union[Parser, ServerError]]:
    """Get hints for the proposed parser of an item

    Get hints for setting the parser settings for the provided
    item. This includes choices or default values that are
    recommended for the item.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (Union['ItemParser', None]):  Example: {'name': 'auto'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Parser, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["ItemParser", None],
) -> Union[Parser]:
    """Get hints for the proposed parser of an item

    Get hints for setting the parser settings for the provided
    item. This includes choices or default values that are
    recommended for the item.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (Union['ItemParser', None]):  Example: {'name': 'auto'}.

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Parser]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["ItemParser", None],
) -> Response[Union[Parser, ServerError]]:
    """Get hints for the proposed parser of an item

    Get hints for setting the parser settings for the provided
    item. This includes choices or default values that are
    recommended for the item.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (Union['ItemParser', None]):  Example: {'name': 'auto'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Parser, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["ItemParser", None],
) -> Union[Parser]:
    """Get hints for the proposed parser of an item

    Get hints for setting the parser settings for the provided
    item. This includes choices or default values that are
    recommended for the item.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (Union['ItemParser', None]):  Example: {'name': 'auto'}.

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Parser]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
