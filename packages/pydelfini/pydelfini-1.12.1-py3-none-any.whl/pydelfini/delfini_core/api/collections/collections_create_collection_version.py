"""Create a new immutable version of an existing collection"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collection import Collection
from ...models.new_collection_version import NewCollectionVersion
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    *,
    body: NewCollectionVersion,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/LIVE".format(
            collection_id=collection_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Collection, ServerError]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = Collection.from_dict(response.json())

        return response_201
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
) -> Response[Union[Collection, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: NewCollectionVersion,
) -> Response[Union[Collection, ServerError]]:
    """Create a new immutable version of an existing collection

    This method is used to create an immutable version of a
    collection. The resulting collection version will be a
    read-only copy of the provided collection ID.

    Optionally, in the request body, a list of `itemIds` can be
    specified which will cause the new version to only include the
    items listed, which must be drawn from the set of items
    already present in the collection.

    Args:
        collection_id (str):
        body (NewCollectionVersion): Collection version details

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Collection, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: NewCollectionVersion,
) -> Union[Collection]:
    """Create a new immutable version of an existing collection

    This method is used to create an immutable version of a
    collection. The resulting collection version will be a
    read-only copy of the provided collection ID.

    Optionally, in the request body, a list of `itemIds` can be
    specified which will cause the new version to only include the
    items listed, which must be drawn from the set of items
    already present in the collection.

    Args:
        collection_id (str):
        body (NewCollectionVersion): Collection version details

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Collection]
    """

    response = sync_detailed(
        collection_id=collection_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: NewCollectionVersion,
) -> Response[Union[Collection, ServerError]]:
    """Create a new immutable version of an existing collection

    This method is used to create an immutable version of a
    collection. The resulting collection version will be a
    read-only copy of the provided collection ID.

    Optionally, in the request body, a list of `itemIds` can be
    specified which will cause the new version to only include the
    items listed, which must be drawn from the set of items
    already present in the collection.

    Args:
        collection_id (str):
        body (NewCollectionVersion): Collection version details

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Collection, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: NewCollectionVersion,
) -> Union[Collection]:
    """Create a new immutable version of an existing collection

    This method is used to create an immutable version of a
    collection. The resulting collection version will be a
    read-only copy of the provided collection ID.

    Optionally, in the request body, a list of `itemIds` can be
    specified which will cause the new version to only include the
    items listed, which must be drawn from the set of items
    already present in the collection.

    Args:
        collection_id (str):
        body (NewCollectionVersion): Collection version details

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Collection]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
