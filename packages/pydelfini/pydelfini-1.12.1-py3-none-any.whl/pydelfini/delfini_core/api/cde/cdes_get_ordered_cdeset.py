"""Get paginated elements and bundles, over this CDE set's preferred order
"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.ordered_dictionary import OrderedDictionary
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    cdeset_name: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/cde/{cdeset_name}".format(
            cdeset_name=cdeset_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[OrderedDictionary, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = OrderedDictionary.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ServerError.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[OrderedDictionary, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    cdeset_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[OrderedDictionary, ServerError]]:
    """Get paginated elements and bundles, over this CDE set's preferred order

    Args:
        cdeset_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[OrderedDictionary, ServerError]]
    """

    kwargs = _get_kwargs(
        cdeset_name=cdeset_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    cdeset_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[OrderedDictionary]:
    """Get paginated elements and bundles, over this CDE set's preferred order

    Args:
        cdeset_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[OrderedDictionary]
    """

    response = sync_detailed(
        cdeset_name=cdeset_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    cdeset_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[OrderedDictionary, ServerError]]:
    """Get paginated elements and bundles, over this CDE set's preferred order

    Args:
        cdeset_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[OrderedDictionary, ServerError]]
    """

    kwargs = _get_kwargs(
        cdeset_name=cdeset_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    cdeset_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[OrderedDictionary]:
    """Get paginated elements and bundles, over this CDE set's preferred order

    Args:
        cdeset_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[OrderedDictionary]
    """

    response = await asyncio_detailed(
        cdeset_name=cdeset_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
