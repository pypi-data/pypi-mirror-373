"""Upload a part of a multipart item upload to a local datastore"""
from http import HTTPStatus
from typing import Any
from typing import cast
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.server_error import ServerError
from ...types import File
from ...types import Response


def _get_kwargs(
    datastore: str,
    upload_id: str,
    part_number: int,
    *,
    body: File,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": "/datastores/{datastore}/uploadPart/{upload_id}/{part_number}".format(
            datastore=datastore,
            upload_id=upload_id,
            part_number=part_number,
        ),
    }

    _body = body.payload

    _kwargs["content"] = _body
    headers["Content-Type"] = "application/octet-stream"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Any, ServerError]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, {"attribute": "None", "return_type": "None"})
        return response_204
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ServerError.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    datastore: str,
    upload_id: str,
    part_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: File,
) -> Response[Union[Any, ServerError]]:
    """Upload a part of a multipart item upload to a local datastore

    For local (filesystem-based) datastores, this will be the
    endpoint that you can use to upload individual parts of a
    multipart item upload. Before sending parts to this endpoint,
    you will need to call `initiate_multipart_upload` for the
    desired collection and item ID; it will provide URLs to this
    endpoint.

    Args:
        datastore (str):
        upload_id (str):
        part_number (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
    """

    kwargs = _get_kwargs(
        datastore=datastore,
        upload_id=upload_id,
        part_number=part_number,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    datastore: str,
    upload_id: str,
    part_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: File,
) -> Union[Any]:
    """Upload a part of a multipart item upload to a local datastore

    For local (filesystem-based) datastores, this will be the
    endpoint that you can use to upload individual parts of a
    multipart item upload. Before sending parts to this endpoint,
    you will need to call `initiate_multipart_upload` for the
    desired collection and item ID; it will provide URLs to this
    endpoint.

    Args:
        datastore (str):
        upload_id (str):
        part_number (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
    """

    response = sync_detailed(
        datastore=datastore,
        upload_id=upload_id,
        part_number=part_number,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    datastore: str,
    upload_id: str,
    part_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: File,
) -> Response[Union[Any, ServerError]]:
    """Upload a part of a multipart item upload to a local datastore

    For local (filesystem-based) datastores, this will be the
    endpoint that you can use to upload individual parts of a
    multipart item upload. Before sending parts to this endpoint,
    you will need to call `initiate_multipart_upload` for the
    desired collection and item ID; it will provide URLs to this
    endpoint.

    Args:
        datastore (str):
        upload_id (str):
        part_number (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
    """

    kwargs = _get_kwargs(
        datastore=datastore,
        upload_id=upload_id,
        part_number=part_number,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    datastore: str,
    upload_id: str,
    part_number: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: File,
) -> Union[Any]:
    """Upload a part of a multipart item upload to a local datastore

    For local (filesystem-based) datastores, this will be the
    endpoint that you can use to upload individual parts of a
    multipart item upload. Before sending parts to this endpoint,
    you will need to call `initiate_multipart_upload` for the
    desired collection and item ID; it will provide URLs to this
    endpoint.

    Args:
        datastore (str):
        upload_id (str):
        part_number (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
    """

    response = await asyncio_detailed(
        datastore=datastore,
        upload_id=upload_id,
        part_number=part_number,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
