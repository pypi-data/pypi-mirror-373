"""Initiate a multipart item data upload sequence"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collections_items_initiate_multipart_upload_body import (
    CollectionsItemsInitiateMultipartUploadBody,
)
from ...models.multipart_upload_details import MultipartUploadDetails
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    item_id: str,
    *,
    body: CollectionsItemsInitiateMultipartUploadBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/{version_id}/items/{item_id}/multipartUpload/initiate".format(
            collection_id=collection_id,
            version_id=version_id,
            item_id=item_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[MultipartUploadDetails, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = MultipartUploadDetails.from_dict(response.json())

        return response_200
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
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[MultipartUploadDetails, ServerError]]:
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
    body: CollectionsItemsInitiateMultipartUploadBody,
) -> Response[Union[MultipartUploadDetails, ServerError]]:
    """Initiate a multipart item data upload sequence

    Starts the process of uploading an item's data as a sequence
    of parts. This method will return a mapping of byte ranges to
    URLs; the client should break up the item data into segments
    and upload each segment to the respective URL. Uploads can be
    performed out-of-order and can be retried if an individual
    upload fails. Once all uploads are complete, the
    `complete_multipart_upload' method should be requested.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (CollectionsItemsInitiateMultipartUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MultipartUploadDetails, ServerError]]
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
    body: CollectionsItemsInitiateMultipartUploadBody,
) -> Union[MultipartUploadDetails]:
    """Initiate a multipart item data upload sequence

    Starts the process of uploading an item's data as a sequence
    of parts. This method will return a mapping of byte ranges to
    URLs; the client should break up the item data into segments
    and upload each segment to the respective URL. Uploads can be
    performed out-of-order and can be retried if an individual
    upload fails. Once all uploads are complete, the
    `complete_multipart_upload' method should be requested.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (CollectionsItemsInitiateMultipartUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MultipartUploadDetails]
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
    body: CollectionsItemsInitiateMultipartUploadBody,
) -> Response[Union[MultipartUploadDetails, ServerError]]:
    """Initiate a multipart item data upload sequence

    Starts the process of uploading an item's data as a sequence
    of parts. This method will return a mapping of byte ranges to
    URLs; the client should break up the item data into segments
    and upload each segment to the respective URL. Uploads can be
    performed out-of-order and can be retried if an individual
    upload fails. Once all uploads are complete, the
    `complete_multipart_upload' method should be requested.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (CollectionsItemsInitiateMultipartUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MultipartUploadDetails, ServerError]]
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
    body: CollectionsItemsInitiateMultipartUploadBody,
) -> Union[MultipartUploadDetails]:
    """Initiate a multipart item data upload sequence

    Starts the process of uploading an item's data as a sequence
    of parts. This method will return a mapping of byte ranges to
    URLs; the client should break up the item data into segments
    and upload each segment to the respective URL. Uploads can be
    performed out-of-order and can be retried if an individual
    upload fails. Once all uploads are complete, the
    `complete_multipart_upload' method should be requested.

    Args:
        collection_id (str):
        version_id (str):
        item_id (str):
        body (CollectionsItemsInitiateMultipartUploadBody):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MultipartUploadDetails]
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
