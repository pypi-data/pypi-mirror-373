"""Receive a federated message by a collection"""
from http import HTTPStatus
from typing import Any
from typing import cast
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.federation_activity import FederationActivity
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    collection_id: str,
    version_id: str,
    *,
    body: Union[
        FederationActivity,
        FederationActivity,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/collections/{collection_id}/{version_id}/inbox".format(
            collection_id=collection_id,
            version_id=version_id,
        ),
    }

    if isinstance(body, FederationActivity):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/activity+json"
    if isinstance(body, FederationActivity):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"

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
) -> Response[Union[Any, ServerError]]:
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
        FederationActivity,
        FederationActivity,
    ],
) -> Response[Union[Any, ServerError]]:
    """Receive a federated message by a collection

    This method is primarily for handling activities coming from
    federated sources. Users creating activities to perform
    actions on collections should post them to their own inbox
    with the proper addressing.

    Args:
        collection_id (str):
        version_id (str):
        body (FederationActivity):
        body (FederationActivity):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
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
        FederationActivity,
        FederationActivity,
    ],
) -> Union[Any]:
    """Receive a federated message by a collection

    This method is primarily for handling activities coming from
    federated sources. Users creating activities to perform
    actions on collections should post them to their own inbox
    with the proper addressing.

    Args:
        collection_id (str):
        version_id (str):
        body (FederationActivity):
        body (FederationActivity):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
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
        FederationActivity,
        FederationActivity,
    ],
) -> Response[Union[Any, ServerError]]:
    """Receive a federated message by a collection

    This method is primarily for handling activities coming from
    federated sources. Users creating activities to perform
    actions on collections should post them to their own inbox
    with the proper addressing.

    Args:
        collection_id (str):
        version_id (str):
        body (FederationActivity):
        body (FederationActivity):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
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
        FederationActivity,
        FederationActivity,
    ],
) -> Union[Any]:
    """Receive a federated message by a collection

    This method is primarily for handling activities coming from
    federated sources. Users creating activities to perform
    actions on collections should post them to their own inbox
    with the proper addressing.

    Args:
        collection_id (str):
        version_id (str):
        body (FederationActivity):
        body (FederationActivity):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
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
