"""Copy an item into this collection"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_items_copy_item_body import CollectionsItemsCopyItemBody
from ...models.item import Item
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    *,
    body: CollectionsItemsCopyItemBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/{version_id}/items/copy".format(
            collection_id=collection_id,
            version_id=version_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Item, ServerError]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = Item.from_dict(response.json())

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
    if response.status_code == HTTPStatus.CONFLICT:
        response_409 = ServerError.from_dict(response.json())

        return response_409
    if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
        response_415 = ServerError.from_dict(response.json())

        return response_415
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Item, ServerError]]:
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
    body: CollectionsItemsCopyItemBody,
) -> Response[Union[Item, ServerError]]:
    """Copy an item into this collection

    Copy an item from a local or remote source into this collection.

    The source item must be specified as a delfini:// URL, and the
    user creating the copy must have read access to the source
    item. The new item name can be specified, along with the
    destination folder; all other metadata changes must be done
    once the item copy is complete.

    All item types support being copied:

    * Copied file and dataviews will share the same
      delfini+datastore:// target, preventing a duplicate copy of
      the data from being stored in the datastore. Copies will not
      affect each other, though, as all writes to file items
      result in a new delfini+datastore:// URL.

    * Links will copy their storage target URLs, and no data will
      be copied.

    * Folders can be copied, however, their contents are not
      recursively copied. To copy an entire folder structure,
      clients should follow a recursive breadth-first algorithm to
      copy the folder, followed by its contents.

    * Dataviews can be copied, however, their data sources will
      not automatically map to new data sources if they are copied
      to a new collection. Clients should assist users to remap
      dataview sources if/when those sources are broken.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCopyItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Item, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        body=body,
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
    body: CollectionsItemsCopyItemBody,
) -> Union[Item]:
    """Copy an item into this collection

    Copy an item from a local or remote source into this collection.

    The source item must be specified as a delfini:// URL, and the
    user creating the copy must have read access to the source
    item. The new item name can be specified, along with the
    destination folder; all other metadata changes must be done
    once the item copy is complete.

    All item types support being copied:

    * Copied file and dataviews will share the same
      delfini+datastore:// target, preventing a duplicate copy of
      the data from being stored in the datastore. Copies will not
      affect each other, though, as all writes to file items
      result in a new delfini+datastore:// URL.

    * Links will copy their storage target URLs, and no data will
      be copied.

    * Folders can be copied, however, their contents are not
      recursively copied. To copy an entire folder structure,
      clients should follow a recursive breadth-first algorithm to
      copy the folder, followed by its contents.

    * Dataviews can be copied, however, their data sources will
      not automatically map to new data sources if they are copied
      to a new collection. Clients should assist users to remap
      dataview sources if/when those sources are broken.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCopyItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Item]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
    body: CollectionsItemsCopyItemBody,
) -> Response[Union[Item, ServerError]]:
    """Copy an item into this collection

    Copy an item from a local or remote source into this collection.

    The source item must be specified as a delfini:// URL, and the
    user creating the copy must have read access to the source
    item. The new item name can be specified, along with the
    destination folder; all other metadata changes must be done
    once the item copy is complete.

    All item types support being copied:

    * Copied file and dataviews will share the same
      delfini+datastore:// target, preventing a duplicate copy of
      the data from being stored in the datastore. Copies will not
      affect each other, though, as all writes to file items
      result in a new delfini+datastore:// URL.

    * Links will copy their storage target URLs, and no data will
      be copied.

    * Folders can be copied, however, their contents are not
      recursively copied. To copy an entire folder structure,
      clients should follow a recursive breadth-first algorithm to
      copy the folder, followed by its contents.

    * Dataviews can be copied, however, their data sources will
      not automatically map to new data sources if they are copied
      to a new collection. Clients should assist users to remap
      dataview sources if/when those sources are broken.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCopyItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Item, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
    body: CollectionsItemsCopyItemBody,
) -> Union[Item]:
    """Copy an item into this collection

    Copy an item from a local or remote source into this collection.

    The source item must be specified as a delfini:// URL, and the
    user creating the copy must have read access to the source
    item. The new item name can be specified, along with the
    destination folder; all other metadata changes must be done
    once the item copy is complete.

    All item types support being copied:

    * Copied file and dataviews will share the same
      delfini+datastore:// target, preventing a duplicate copy of
      the data from being stored in the datastore. Copies will not
      affect each other, though, as all writes to file items
      result in a new delfini+datastore:// URL.

    * Links will copy their storage target URLs, and no data will
      be copied.

    * Folders can be copied, however, their contents are not
      recursively copied. To copy an entire folder structure,
      clients should follow a recursive breadth-first algorithm to
      copy the folder, followed by its contents.

    * Dataviews can be copied, however, their data sources will
      not automatically map to new data sources if they are copied
      to a new collection. Clients should assist users to remap
      dataview sources if/when those sources are broken.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCopyItemBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Item]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
