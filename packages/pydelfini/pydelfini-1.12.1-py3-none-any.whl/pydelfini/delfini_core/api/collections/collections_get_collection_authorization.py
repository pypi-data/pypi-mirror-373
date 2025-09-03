"""Get collection authorized users and groups"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collection_authorization import CollectionAuthorization
from ...models.collections_get_collection_authorization_filter import (
    CollectionsGetCollectionAuthorizationFilter,
)
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    collection_id: str,
    version_id: str,
    *,
    filter_: Union[Unset, CollectionsGetCollectionAuthorizationFilter] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_filter_: Union[Unset, str] = UNSET
    if not isinstance(filter_, Unset):
        json_filter_ = filter_.value

    params["filter"] = json_filter_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/authorization".format(
            collection_id=collection_id,
            version_id=version_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[CollectionAuthorization, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectionAuthorization.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ServerError.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ServerError.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CollectionAuthorization, ServerError]]:
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
    filter_: Union[Unset, CollectionsGetCollectionAuthorizationFilter] = UNSET,
) -> Response[Union[CollectionAuthorization, ServerError]]:
    """Get collection authorized users and groups

    Args:
        collection_id (str):
        version_id (str):
        filter_ (Union[Unset, CollectionsGetCollectionAuthorizationFilter]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionAuthorization, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        filter_=filter_,
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
    filter_: Union[Unset, CollectionsGetCollectionAuthorizationFilter] = UNSET,
) -> Union[CollectionAuthorization]:
    """Get collection authorized users and groups

    Args:
        collection_id (str):
        version_id (str):
        filter_ (Union[Unset, CollectionsGetCollectionAuthorizationFilter]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionAuthorization]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
        filter_=filter_,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
    filter_: Union[Unset, CollectionsGetCollectionAuthorizationFilter] = UNSET,
) -> Response[Union[CollectionAuthorization, ServerError]]:
    """Get collection authorized users and groups

    Args:
        collection_id (str):
        version_id (str):
        filter_ (Union[Unset, CollectionsGetCollectionAuthorizationFilter]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionAuthorization, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        filter_=filter_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
    filter_: Union[Unset, CollectionsGetCollectionAuthorizationFilter] = UNSET,
) -> Union[CollectionAuthorization]:
    """Get collection authorized users and groups

    Args:
        collection_id (str):
        version_id (str):
        filter_ (Union[Unset, CollectionsGetCollectionAuthorizationFilter]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionAuthorization]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
        filter_=filter_,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
