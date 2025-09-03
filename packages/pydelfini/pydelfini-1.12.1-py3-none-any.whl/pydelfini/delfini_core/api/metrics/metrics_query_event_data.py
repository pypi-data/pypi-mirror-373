"""Retrieve real-time aggregated metric data from an event"""
import datetime
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.metric_agg_func import MetricAggFunc
from ...models.metric_data import MetricData
from ...models.metrics_query_event_data_period import MetricsQueryEventDataPeriod
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    event_name: str,
    *,
    dimension: Union[Unset, str] = UNSET,
    period: MetricsQueryEventDataPeriod,
    agg_func: MetricAggFunc,
    partition_by: Union[Unset, str] = UNSET,
    num_partitions: Union[Unset, int] = UNSET,
    start: Union[Unset, datetime.datetime] = UNSET,
    end: Union[Unset, datetime.datetime] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["dimension"] = dimension

    json_period = period.value
    params["period"] = json_period

    json_agg_func = agg_func.value
    params["agg_func"] = json_agg_func

    params["partition_by"] = partition_by

    params["num_partitions"] = num_partitions

    json_start: Union[Unset, str] = UNSET
    if not isinstance(start, Unset):
        json_start = start.isoformat()
    params["start"] = json_start

    json_end: Union[Unset, str] = UNSET
    if not isinstance(end, Unset):
        json_end = end.isoformat()
    params["end"] = json_end

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/metrics/events/{event_name}/data".format(
            event_name=event_name,
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
    event_name: str,
    *,
    client: AuthenticatedClient,
    dimension: Union[Unset, str] = UNSET,
    period: MetricsQueryEventDataPeriod,
    agg_func: MetricAggFunc,
    partition_by: Union[Unset, str] = UNSET,
    num_partitions: Union[Unset, int] = UNSET,
    start: Union[Unset, datetime.datetime] = UNSET,
    end: Union[Unset, datetime.datetime] = UNSET,
) -> Response[Union[MetricData, ServerError]]:
    """Retrieve real-time aggregated metric data from an event

    Args:
        event_name (str):
        dimension (Union[Unset, str]):
        period (MetricsQueryEventDataPeriod):
        agg_func (MetricAggFunc):
        partition_by (Union[Unset, str]):
        num_partitions (Union[Unset, int]):
        start (Union[Unset, datetime.datetime]):
        end (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MetricData, ServerError]]
    """

    kwargs = _get_kwargs(
        event_name=event_name,
        dimension=dimension,
        period=period,
        agg_func=agg_func,
        partition_by=partition_by,
        num_partitions=num_partitions,
        start=start,
        end=end,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    event_name: str,
    *,
    client: AuthenticatedClient,
    dimension: Union[Unset, str] = UNSET,
    period: MetricsQueryEventDataPeriod,
    agg_func: MetricAggFunc,
    partition_by: Union[Unset, str] = UNSET,
    num_partitions: Union[Unset, int] = UNSET,
    start: Union[Unset, datetime.datetime] = UNSET,
    end: Union[Unset, datetime.datetime] = UNSET,
) -> Union[MetricData]:
    """Retrieve real-time aggregated metric data from an event

    Args:
        event_name (str):
        dimension (Union[Unset, str]):
        period (MetricsQueryEventDataPeriod):
        agg_func (MetricAggFunc):
        partition_by (Union[Unset, str]):
        num_partitions (Union[Unset, int]):
        start (Union[Unset, datetime.datetime]):
        end (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MetricData]
    """

    response = sync_detailed(
        event_name=event_name,
        client=client,
        dimension=dimension,
        period=period,
        agg_func=agg_func,
        partition_by=partition_by,
        num_partitions=num_partitions,
        start=start,
        end=end,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    event_name: str,
    *,
    client: AuthenticatedClient,
    dimension: Union[Unset, str] = UNSET,
    period: MetricsQueryEventDataPeriod,
    agg_func: MetricAggFunc,
    partition_by: Union[Unset, str] = UNSET,
    num_partitions: Union[Unset, int] = UNSET,
    start: Union[Unset, datetime.datetime] = UNSET,
    end: Union[Unset, datetime.datetime] = UNSET,
) -> Response[Union[MetricData, ServerError]]:
    """Retrieve real-time aggregated metric data from an event

    Args:
        event_name (str):
        dimension (Union[Unset, str]):
        period (MetricsQueryEventDataPeriod):
        agg_func (MetricAggFunc):
        partition_by (Union[Unset, str]):
        num_partitions (Union[Unset, int]):
        start (Union[Unset, datetime.datetime]):
        end (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MetricData, ServerError]]
    """

    kwargs = _get_kwargs(
        event_name=event_name,
        dimension=dimension,
        period=period,
        agg_func=agg_func,
        partition_by=partition_by,
        num_partitions=num_partitions,
        start=start,
        end=end,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_name: str,
    *,
    client: AuthenticatedClient,
    dimension: Union[Unset, str] = UNSET,
    period: MetricsQueryEventDataPeriod,
    agg_func: MetricAggFunc,
    partition_by: Union[Unset, str] = UNSET,
    num_partitions: Union[Unset, int] = UNSET,
    start: Union[Unset, datetime.datetime] = UNSET,
    end: Union[Unset, datetime.datetime] = UNSET,
) -> Union[MetricData]:
    """Retrieve real-time aggregated metric data from an event

    Args:
        event_name (str):
        dimension (Union[Unset, str]):
        period (MetricsQueryEventDataPeriod):
        agg_func (MetricAggFunc):
        partition_by (Union[Unset, str]):
        num_partitions (Union[Unset, int]):
        start (Union[Unset, datetime.datetime]):
        end (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MetricData]
    """

    response = await asyncio_detailed(
        event_name=event_name,
        client=client,
        dimension=dimension,
        period=period,
        agg_func=agg_func,
        partition_by=partition_by,
        num_partitions=num_partitions,
        start=start,
        end=end,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
