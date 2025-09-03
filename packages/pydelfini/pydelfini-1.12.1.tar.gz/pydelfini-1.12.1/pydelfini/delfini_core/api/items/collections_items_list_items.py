"""List items or find items by properties"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_items_list_items_response_200 import (
    CollectionsItemsListItemsResponse200,
)
from ...models.item_type import ItemType
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    collection_id: str,
    version_id: str,
    *,
    name: Union[Unset, str] = UNSET,
    type: Union[Unset, List[ItemType]] = UNSET,
    in_folder: Union[Unset, str] = UNSET,
    in_path: Union[Unset, str] = UNSET,
    parsable: Union[Unset, bool] = UNSET,
    is_failed: Union[Unset, bool] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["name"] = name

    json_type: Union[Unset, List[str]] = UNSET
    if not isinstance(type, Unset):
        json_type = []
        for type_item_data in type:
            type_item = type_item_data.value
            json_type.append(type_item)

    params["type"] = json_type

    params["in_folder"] = in_folder

    params["in_path"] = in_path

    params["parsable"] = parsable

    params["is_failed"] = is_failed

    params["meta"] = meta

    params["bmeta"] = bmeta

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/items".format(
            collection_id=collection_id,
            version_id=version_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[CollectionsItemsListItemsResponse200, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectionsItemsListItemsResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ServerError.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ServerError.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
        response_415 = ServerError.from_dict(response.json())

        return response_415
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CollectionsItemsListItemsResponse200, ServerError]]:
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
    name: Union[Unset, str] = UNSET,
    type: Union[Unset, List[ItemType]] = UNSET,
    in_folder: Union[Unset, str] = UNSET,
    in_path: Union[Unset, str] = UNSET,
    parsable: Union[Unset, bool] = UNSET,
    is_failed: Union[Unset, bool] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Response[Union[CollectionsItemsListItemsResponse200, ServerError]]:
    """List items or find items by properties

    Find one or more items as part of the collection (and version ID).

    Query filters are combined with the AND operator. Multiple
    values may be supplied for each filter and will be combined
    with the OR operator.

    The resulting list of items will include the storage, parser,
    and status fields, but the columns field will always be `null`
    since some items may have a large number of columns.

    Args:
        collection_id (str):
        version_id (str):
        name (Union[Unset, str]):
        type (Union[Unset, List[ItemType]]):
        in_folder (Union[Unset, str]):
        in_path (Union[Unset, str]):
        parsable (Union[Unset, bool]):
        is_failed (Union[Unset, bool]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsItemsListItemsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        name=name,
        type=type,
        in_folder=in_folder,
        in_path=in_path,
        parsable=parsable,
        is_failed=is_failed,
        meta=meta,
        bmeta=bmeta,
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
    name: Union[Unset, str] = UNSET,
    type: Union[Unset, List[ItemType]] = UNSET,
    in_folder: Union[Unset, str] = UNSET,
    in_path: Union[Unset, str] = UNSET,
    parsable: Union[Unset, bool] = UNSET,
    is_failed: Union[Unset, bool] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Union[CollectionsItemsListItemsResponse200]:
    """List items or find items by properties

    Find one or more items as part of the collection (and version ID).

    Query filters are combined with the AND operator. Multiple
    values may be supplied for each filter and will be combined
    with the OR operator.

    The resulting list of items will include the storage, parser,
    and status fields, but the columns field will always be `null`
    since some items may have a large number of columns.

    Args:
        collection_id (str):
        version_id (str):
        name (Union[Unset, str]):
        type (Union[Unset, List[ItemType]]):
        in_folder (Union[Unset, str]):
        in_path (Union[Unset, str]):
        parsable (Union[Unset, bool]):
        is_failed (Union[Unset, bool]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsItemsListItemsResponse200]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
        name=name,
        type=type,
        in_folder=in_folder,
        in_path=in_path,
        parsable=parsable,
        is_failed=is_failed,
        meta=meta,
        bmeta=bmeta,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    type: Union[Unset, List[ItemType]] = UNSET,
    in_folder: Union[Unset, str] = UNSET,
    in_path: Union[Unset, str] = UNSET,
    parsable: Union[Unset, bool] = UNSET,
    is_failed: Union[Unset, bool] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Response[Union[CollectionsItemsListItemsResponse200, ServerError]]:
    """List items or find items by properties

    Find one or more items as part of the collection (and version ID).

    Query filters are combined with the AND operator. Multiple
    values may be supplied for each filter and will be combined
    with the OR operator.

    The resulting list of items will include the storage, parser,
    and status fields, but the columns field will always be `null`
    since some items may have a large number of columns.

    Args:
        collection_id (str):
        version_id (str):
        name (Union[Unset, str]):
        type (Union[Unset, List[ItemType]]):
        in_folder (Union[Unset, str]):
        in_path (Union[Unset, str]):
        parsable (Union[Unset, bool]):
        is_failed (Union[Unset, bool]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionsItemsListItemsResponse200, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        name=name,
        type=type,
        in_folder=in_folder,
        in_path=in_path,
        parsable=parsable,
        is_failed=is_failed,
        meta=meta,
        bmeta=bmeta,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    type: Union[Unset, List[ItemType]] = UNSET,
    in_folder: Union[Unset, str] = UNSET,
    in_path: Union[Unset, str] = UNSET,
    parsable: Union[Unset, bool] = UNSET,
    is_failed: Union[Unset, bool] = UNSET,
    meta: Union[Unset, str] = UNSET,
    bmeta: Union[Unset, str] = UNSET,
) -> Union[CollectionsItemsListItemsResponse200]:
    """List items or find items by properties

    Find one or more items as part of the collection (and version ID).

    Query filters are combined with the AND operator. Multiple
    values may be supplied for each filter and will be combined
    with the OR operator.

    The resulting list of items will include the storage, parser,
    and status fields, but the columns field will always be `null`
    since some items may have a large number of columns.

    Args:
        collection_id (str):
        version_id (str):
        name (Union[Unset, str]):
        type (Union[Unset, List[ItemType]]):
        in_folder (Union[Unset, str]):
        in_path (Union[Unset, str]):
        parsable (Union[Unset, bool]):
        is_failed (Union[Unset, bool]):
        meta (Union[Unset, str]):
        bmeta (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionsItemsListItemsResponse200]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        client=client,
        name=name,
        type=type,
        in_folder=in_folder,
        in_path=in_path,
        parsable=parsable,
        is_failed=is_failed,
        meta=meta,
        bmeta=bmeta,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
