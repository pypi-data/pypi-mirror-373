"""Retrieve the contents of an item"""
from http import HTTPStatus
from io import BytesIO
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_items_get_item_data_dl import CollectionsItemsGetItemDataDl
from ...models.server_error import ServerError
from ...types import File
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    dl: Union[Unset, CollectionsItemsGetItemDataDl] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_dl: Union[Unset, str] = UNSET
    if not isinstance(dl, Unset):
        json_dl = dl.value

    params["dl"] = json_dl

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/items/{item_id}/data".format(
            collection_id=collection_id,
            version_id=version_id,
            item_id=item_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[File, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = File(payload=BytesIO(response.content))

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
) -> Response[Union[File, ServerError]]:
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
    dl: Union[Unset, CollectionsItemsGetItemDataDl] = UNSET,
) -> Response[Union[File, ServerError]]:
    """Retrieve the contents of an item

    Retrieve the body of an item.

    Not valid on folders.

    For dataviews, this method retrieves the dataview's definition code.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        dl (Union[Unset, CollectionsItemsGetItemDataDl]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[File, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        dl=dl,
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
    dl: Union[Unset, CollectionsItemsGetItemDataDl] = UNSET,
) -> Union[File]:
    """Retrieve the contents of an item

    Retrieve the body of an item.

    Not valid on folders.

    For dataviews, this method retrieves the dataview's definition code.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        dl (Union[Unset, CollectionsItemsGetItemDataDl]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[File]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        client=client,
        dl=dl,
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
    dl: Union[Unset, CollectionsItemsGetItemDataDl] = UNSET,
) -> Response[Union[File, ServerError]]:
    """Retrieve the contents of an item

    Retrieve the body of an item.

    Not valid on folders.

    For dataviews, this method retrieves the dataview's definition code.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        dl (Union[Unset, CollectionsItemsGetItemDataDl]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[File, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        dl=dl,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    client: AuthenticatedClient,
    dl: Union[Unset, CollectionsItemsGetItemDataDl] = UNSET,
) -> Union[File]:
    """Retrieve the contents of an item

    Retrieve the body of an item.

    Not valid on folders.

    For dataviews, this method retrieves the dataview's definition code.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        dl (Union[Unset, CollectionsItemsGetItemDataDl]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[File]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        client=client,
        dl=dl,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
