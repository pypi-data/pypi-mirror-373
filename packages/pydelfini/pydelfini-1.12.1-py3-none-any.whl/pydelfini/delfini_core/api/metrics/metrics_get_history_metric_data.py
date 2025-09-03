"""Retrieve metric history data"""
import datetime
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.metric_data import MetricData
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET


def _get_kwargs(
    metric_name: str,
    *,
    start: datetime.datetime,
    end: datetime.datetime,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_start = start.isoformat()
    params["start"] = json_start

    json_end = end.isoformat()
    params["end"] = json_end

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/metrics/history/{metric_name}/data".format(
            metric_name=metric_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[MetricData, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = MetricData.from_dict(response.json())

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
) -> Response[Union[MetricData, ServerError]]:
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
    start: datetime.datetime,
    end: datetime.datetime,
) -> Response[Union[MetricData, ServerError]]:
    """Retrieve metric history data

    Args:
        metric_name (str):
        start (datetime.datetime):
        end (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MetricData, ServerError]]
    """

    kwargs = _get_kwargs(
        metric_name=metric_name,
        start=start,
        end=end,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    metric_name: str,
    *,
    client: AuthenticatedClient,
    start: datetime.datetime,
    end: datetime.datetime,
) -> Union[MetricData]:
    """Retrieve metric history data

    Args:
        metric_name (str):
        start (datetime.datetime):
        end (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MetricData]
    """

    response = sync_detailed(
        metric_name=metric_name,
        client=client,
        start=start,
        end=end,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    metric_name: str,
    *,
    client: AuthenticatedClient,
    start: datetime.datetime,
    end: datetime.datetime,
) -> Response[Union[MetricData, ServerError]]:
    """Retrieve metric history data

    Args:
        metric_name (str):
        start (datetime.datetime):
        end (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MetricData, ServerError]]
    """

    kwargs = _get_kwargs(
        metric_name=metric_name,
        start=start,
        end=end,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    metric_name: str,
    *,
    client: AuthenticatedClient,
    start: datetime.datetime,
    end: datetime.datetime,
) -> Union[MetricData]:
    """Retrieve metric history data

    Args:
        metric_name (str):
        start (datetime.datetime):
        end (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MetricData]
    """

    response = await asyncio_detailed(
        metric_name=metric_name,
        client=client,
        start=start,
        end=end,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
