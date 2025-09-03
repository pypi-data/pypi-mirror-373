"""List projects"""
from http import HTTPStatus
from typing import Any
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.projects_get_projects_project_list import ProjectsGetProjectsProjectList
from ...models.server_error import ServerError
from ...types import Response
from ...types import UNSET
from ...types import Unset


def _get_kwargs(
    *,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["name"] = name

    params["account_id"] = account_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ProjectsGetProjectsProjectList, ServerError]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ProjectsGetProjectsProjectList.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ProjectsGetProjectsProjectList, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Response[Union[ProjectsGetProjectsProjectList, ServerError]]:
    """List projects

    List all projects that are visible.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProjectsGetProjectsProjectList, ServerError]]
    """

    kwargs = _get_kwargs(
        name=name,
        account_id=account_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Union[ProjectsGetProjectsProjectList]:
    """List projects

    List all projects that are visible.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProjectsGetProjectsProjectList]
    """

    response = sync_detailed(
        client=client,
        name=name,
        account_id=account_id,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Response[Union[ProjectsGetProjectsProjectList, ServerError]]:
    """List projects

    List all projects that are visible.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProjectsGetProjectsProjectList, ServerError]]
    """

    kwargs = _get_kwargs(
        name=name,
        account_id=account_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Union[ProjectsGetProjectsProjectList]:
    """List projects

    List all projects that are visible.

    Args:
        name (Union[Unset, str]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProjectsGetProjectsProjectList]
    """

    response = await asyncio_detailed(
        client=client,
        name=name,
        account_id=account_id,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
