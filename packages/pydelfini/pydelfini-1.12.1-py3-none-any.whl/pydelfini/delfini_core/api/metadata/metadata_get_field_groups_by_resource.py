"""Retrieve metadata field groups for a particular resource type"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.metadata_field_groups import MetadataFieldGroups
from ...models.metadata_get_field_groups_by_resource_resource_type import (
    MetadataGetFieldGroupsByResourceResourceType,
)
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    resource_type: MetadataGetFieldGroupsByResourceResourceType,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/metadata/fieldGroups/{resource_type}".format(
            resource_type=resource_type,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[MetadataFieldGroups, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = MetadataFieldGroups.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[MetadataFieldGroups, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    resource_type: MetadataGetFieldGroupsByResourceResourceType,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[MetadataFieldGroups, ServerError]]:
    """Retrieve metadata field groups for a particular resource type

    Args:
        resource_type (MetadataGetFieldGroupsByResourceResourceType):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MetadataFieldGroups, ServerError]]
    """

    kwargs = _get_kwargs(
        resource_type=resource_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    resource_type: MetadataGetFieldGroupsByResourceResourceType,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[MetadataFieldGroups]:
    """Retrieve metadata field groups for a particular resource type

    Args:
        resource_type (MetadataGetFieldGroupsByResourceResourceType):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MetadataFieldGroups]
    """

    response = sync_detailed(
        resource_type=resource_type,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    resource_type: MetadataGetFieldGroupsByResourceResourceType,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[MetadataFieldGroups, ServerError]]:
    """Retrieve metadata field groups for a particular resource type

    Args:
        resource_type (MetadataGetFieldGroupsByResourceResourceType):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MetadataFieldGroups, ServerError]]
    """

    kwargs = _get_kwargs(
        resource_type=resource_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    resource_type: MetadataGetFieldGroupsByResourceResourceType,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[MetadataFieldGroups]:
    """Retrieve metadata field groups for a particular resource type

    Args:
        resource_type (MetadataGetFieldGroupsByResourceResourceType):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MetadataFieldGroups]
    """

    response = await asyncio_detailed(
        resource_type=resource_type,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
