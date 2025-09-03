"""Get collection CDE statistics"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.collection_cde_stats import CollectionCdeStats
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    collection_id: str,
    version_id: str,
    cdeset_name: str,
    *,
    byitem: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["byitem"] = byitem

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/collections/{collection_id}/{version_id}/stats/cdes/{cdeset_name}".format(
            collection_id=collection_id,
            version_id=version_id,
            cdeset_name=cdeset_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[CollectionCdeStats, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectionCdeStats.from_dict(response.json())

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
) -> Response[Union[CollectionCdeStats, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    version_id: str,
    cdeset_name: str,
    *,
    client: AuthenticatedClient,
    byitem: Union[Unset, bool] = UNSET,
) -> Response[Union[CollectionCdeStats, ServerError]]:
    """Get collection CDE statistics

    Args:
        collection_id (str):
        version_id (str):
        cdeset_name (str):
        byitem (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionCdeStats, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        cdeset_name=cdeset_name,
        byitem=byitem,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    version_id: str,
    cdeset_name: str,
    *,
    client: AuthenticatedClient,
    byitem: Union[Unset, bool] = UNSET,
) -> Union[CollectionCdeStats]:
    """Get collection CDE statistics

    Args:
        collection_id (str):
        version_id (str):
        cdeset_name (str):
        byitem (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionCdeStats]
    """

    response = sync_detailed(
        collection_id=collection_id,
        version_id=version_id,
        cdeset_name=cdeset_name,
        client=client,
        byitem=byitem,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    version_id: str,
    cdeset_name: str,
    *,
    client: AuthenticatedClient,
    byitem: Union[Unset, bool] = UNSET,
) -> Response[Union[CollectionCdeStats, ServerError]]:
    """Get collection CDE statistics

    Args:
        collection_id (str):
        version_id (str):
        cdeset_name (str):
        byitem (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectionCdeStats, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        version_id=version_id,
        cdeset_name=cdeset_name,
        byitem=byitem,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    version_id: str,
    cdeset_name: str,
    *,
    client: AuthenticatedClient,
    byitem: Union[Unset, bool] = UNSET,
) -> Union[CollectionCdeStats]:
    """Get collection CDE statistics

    Args:
        collection_id (str):
        version_id (str):
        cdeset_name (str):
        byitem (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectionCdeStats]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        version_id=version_id,
        cdeset_name=cdeset_name,
        client=client,
        byitem=byitem,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
