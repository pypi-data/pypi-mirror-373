"""Get details for a metric"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.event_metric import EventMetric
from ...models.metadata_metric import MetadataMetric
from ...models.server_error import ServerError
from ...types import Response


def _get_kwargs(
    metric_name: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/metrics/history/{metric_name}".format(
            metric_name=metric_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ServerError, Union["EventMetric", "MetadataMetric"]]:
    if response.status_code == HTTPStatus.OK:

        def _parse_response_200(data: object) -> Union["EventMetric", "MetadataMetric"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasmetric_type_0 = MetadataMetric.from_dict(data)

                return componentsschemasmetric_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemasmetric_type_1 = EventMetric.from_dict(data)

            return componentsschemasmetric_type_1

        response_200 = _parse_response_200(response.json())

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
) -> Response[Union[ServerError, Union["EventMetric", "MetadataMetric"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    metric_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, Union["EventMetric", "MetadataMetric"]]]:
    """Get details for a metric

    Args:
        metric_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, Union['EventMetric', 'MetadataMetric']]]
    """

    kwargs = _get_kwargs(
        metric_name=metric_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    metric_name: str,
    *,
    client: AuthenticatedClient,
) -> Union[Union["EventMetric", "MetadataMetric"]]:
    """Get details for a metric

    Args:
        metric_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Union['EventMetric', 'MetadataMetric']]
    """

    response = sync_detailed(
        metric_name=metric_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    metric_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ServerError, Union["EventMetric", "MetadataMetric"]]]:
    """Get details for a metric

    Args:
        metric_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ServerError, Union['EventMetric', 'MetadataMetric']]]
    """

    kwargs = _get_kwargs(
        metric_name=metric_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    metric_name: str,
    *,
    client: AuthenticatedClient,
) -> Union[Union["EventMetric", "MetadataMetric"]]:
    """Get details for a metric

    Args:
        metric_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Union['EventMetric', 'MetadataMetric']]
    """

    response = await asyncio_detailed(
        metric_name=metric_name,
        client=client,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
