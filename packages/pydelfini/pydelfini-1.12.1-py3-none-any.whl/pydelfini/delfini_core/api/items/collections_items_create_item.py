"""Upload a file, create a link or a folder"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_items_create_item_files_form_style_upload import (
    CollectionsItemsCreateItemFilesFormStyleUpload,
)
from ...models.collections_items_create_item_json_new_item_request import (
    CollectionsItemsCreateItemJsonNewItemRequest,
)
from ...models.item import Item
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    *,
    body: Union[
        CollectionsItemsCreateItemJsonNewItemRequest,
        CollectionsItemsCreateItemFilesFormStyleUpload,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/{version_id}/items".format(
            collection_id=collection_id,
            version_id=version_id,
        ),
    }

    if isinstance(body, CollectionsItemsCreateItemJsonNewItemRequest):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, CollectionsItemsCreateItemFilesFormStyleUpload):
        _files_body = body.to_multipart()

        _kwargs["files"] = _files_body

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
    body: Union[
        CollectionsItemsCreateItemJsonNewItemRequest,
        CollectionsItemsCreateItemFilesFormStyleUpload,
    ],
) -> Response[Union[Item, ServerError]]:
    r"""Upload a file, create a link or a folder

    Create a new item (a file, link, folder, or dataview) given its specification.

    Two request body formats are supported:

    * `application/json` is typically used for links, folders, and
      very small files/dataviews. The item content (for files and
      dataviews) can be specified as a string in the request body,
      under the `content.data` field.

    * `multipart/form-data` is used for larger files. The item
      content should be provided in the form `content` field, and
      the item name will be taken as the `content` field's
      `filename` attribute.

    If provided, the `folderId` attribute should either be a
    string of an existing item ID that references a folder in the
    collection, or else the string \"ROOT\", denoting the top level
    of the collection.

    For files and dataviews, the `storage.url` field should
    reference the URL of an existing datastore defined in the
    system (as listed by the `/datastores` API call). It can be
    assumed that the datastore `delfini+datastore://default` will
    always exist, but users may choose to store their data in an
    alternate datastore.

    For links, the `storage.url` field should reference an
    external resource available through a standard URL scheme such
    as `https://` or `s3://`, or another Delfini resource available
    through the URL scheme
    `delfini://hostname/collection-id/version-id/item-id`.

    If the checksum of a file, link, or dataview is known by the
    client at the time of upload, it can be provided in either the
    `storage.checksum` field (supporting all item types) or the
    `content.checksum` field (supporting just files and
    dataviews).

    If the user desires the item to be parseable as a table, the
    `parser` field should be set, with the name of the parser
    provided as well as optional parser options. Otherwise, the
    `parser` field can remain unset.

    If the user knows or wishes to define the column schema of the
    item, a list of column definitions can be provided in the
    `columns` field. This should be omitted if the item will not
    be parsed as a table.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCreateItemJsonNewItemRequest):
        body (CollectionsItemsCreateItemFilesFormStyleUpload): Creation of a new item

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
    body: Union[
        CollectionsItemsCreateItemJsonNewItemRequest,
        CollectionsItemsCreateItemFilesFormStyleUpload,
    ],
) -> Union[Item]:
    r"""Upload a file, create a link or a folder

    Create a new item (a file, link, folder, or dataview) given its specification.

    Two request body formats are supported:

    * `application/json` is typically used for links, folders, and
      very small files/dataviews. The item content (for files and
      dataviews) can be specified as a string in the request body,
      under the `content.data` field.

    * `multipart/form-data` is used for larger files. The item
      content should be provided in the form `content` field, and
      the item name will be taken as the `content` field's
      `filename` attribute.

    If provided, the `folderId` attribute should either be a
    string of an existing item ID that references a folder in the
    collection, or else the string \"ROOT\", denoting the top level
    of the collection.

    For files and dataviews, the `storage.url` field should
    reference the URL of an existing datastore defined in the
    system (as listed by the `/datastores` API call). It can be
    assumed that the datastore `delfini+datastore://default` will
    always exist, but users may choose to store their data in an
    alternate datastore.

    For links, the `storage.url` field should reference an
    external resource available through a standard URL scheme such
    as `https://` or `s3://`, or another Delfini resource available
    through the URL scheme
    `delfini://hostname/collection-id/version-id/item-id`.

    If the checksum of a file, link, or dataview is known by the
    client at the time of upload, it can be provided in either the
    `storage.checksum` field (supporting all item types) or the
    `content.checksum` field (supporting just files and
    dataviews).

    If the user desires the item to be parseable as a table, the
    `parser` field should be set, with the name of the parser
    provided as well as optional parser options. Otherwise, the
    `parser` field can remain unset.

    If the user knows or wishes to define the column schema of the
    item, a list of column definitions can be provided in the
    `columns` field. This should be omitted if the item will not
    be parsed as a table.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCreateItemJsonNewItemRequest):
        body (CollectionsItemsCreateItemFilesFormStyleUpload): Creation of a new item

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
    body: Union[
        CollectionsItemsCreateItemJsonNewItemRequest,
        CollectionsItemsCreateItemFilesFormStyleUpload,
    ],
) -> Response[Union[Item, ServerError]]:
    r"""Upload a file, create a link or a folder

    Create a new item (a file, link, folder, or dataview) given its specification.

    Two request body formats are supported:

    * `application/json` is typically used for links, folders, and
      very small files/dataviews. The item content (for files and
      dataviews) can be specified as a string in the request body,
      under the `content.data` field.

    * `multipart/form-data` is used for larger files. The item
      content should be provided in the form `content` field, and
      the item name will be taken as the `content` field's
      `filename` attribute.

    If provided, the `folderId` attribute should either be a
    string of an existing item ID that references a folder in the
    collection, or else the string \"ROOT\", denoting the top level
    of the collection.

    For files and dataviews, the `storage.url` field should
    reference the URL of an existing datastore defined in the
    system (as listed by the `/datastores` API call). It can be
    assumed that the datastore `delfini+datastore://default` will
    always exist, but users may choose to store their data in an
    alternate datastore.

    For links, the `storage.url` field should reference an
    external resource available through a standard URL scheme such
    as `https://` or `s3://`, or another Delfini resource available
    through the URL scheme
    `delfini://hostname/collection-id/version-id/item-id`.

    If the checksum of a file, link, or dataview is known by the
    client at the time of upload, it can be provided in either the
    `storage.checksum` field (supporting all item types) or the
    `content.checksum` field (supporting just files and
    dataviews).

    If the user desires the item to be parseable as a table, the
    `parser` field should be set, with the name of the parser
    provided as well as optional parser options. Otherwise, the
    `parser` field can remain unset.

    If the user knows or wishes to define the column schema of the
    item, a list of column definitions can be provided in the
    `columns` field. This should be omitted if the item will not
    be parsed as a table.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCreateItemJsonNewItemRequest):
        body (CollectionsItemsCreateItemFilesFormStyleUpload): Creation of a new item

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
    body: Union[
        CollectionsItemsCreateItemJsonNewItemRequest,
        CollectionsItemsCreateItemFilesFormStyleUpload,
    ],
) -> Union[Item]:
    r"""Upload a file, create a link or a folder

    Create a new item (a file, link, folder, or dataview) given its specification.

    Two request body formats are supported:

    * `application/json` is typically used for links, folders, and
      very small files/dataviews. The item content (for files and
      dataviews) can be specified as a string in the request body,
      under the `content.data` field.

    * `multipart/form-data` is used for larger files. The item
      content should be provided in the form `content` field, and
      the item name will be taken as the `content` field's
      `filename` attribute.

    If provided, the `folderId` attribute should either be a
    string of an existing item ID that references a folder in the
    collection, or else the string \"ROOT\", denoting the top level
    of the collection.

    For files and dataviews, the `storage.url` field should
    reference the URL of an existing datastore defined in the
    system (as listed by the `/datastores` API call). It can be
    assumed that the datastore `delfini+datastore://default` will
    always exist, but users may choose to store their data in an
    alternate datastore.

    For links, the `storage.url` field should reference an
    external resource available through a standard URL scheme such
    as `https://` or `s3://`, or another Delfini resource available
    through the URL scheme
    `delfini://hostname/collection-id/version-id/item-id`.

    If the checksum of a file, link, or dataview is known by the
    client at the time of upload, it can be provided in either the
    `storage.checksum` field (supporting all item types) or the
    `content.checksum` field (supporting just files and
    dataviews).

    If the user desires the item to be parseable as a table, the
    `parser` field should be set, with the name of the parser
    provided as well as optional parser options. Otherwise, the
    `parser` field can remain unset.

    If the user knows or wishes to define the column schema of the
    item, a list of column definitions can be provided in the
    `columns` field. This should be omitted if the item will not
    be parsed as a table.

    Args:
        collection_id (str):
        version_id (str):
        body (CollectionsItemsCreateItemJsonNewItemRequest):
        body (CollectionsItemsCreateItemFilesFormStyleUpload): Creation of a new item

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
