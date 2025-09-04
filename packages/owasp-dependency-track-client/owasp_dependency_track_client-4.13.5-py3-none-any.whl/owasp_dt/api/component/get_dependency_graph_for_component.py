from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_dependency_graph_for_component_response_200 import (
    GetDependencyGraphForComponentResponse200,
)
from ...types import Response


def _get_kwargs(
    project_uuid: UUID,
    component_uuids: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/component/project/{project_uuid}/dependencyGraph/{component_uuids}".format(
            project_uuid=project_uuid,
            component_uuids=component_uuids,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, GetDependencyGraphForComponentResponse200]]:
    if response.status_code == 200:
        response_200 = GetDependencyGraphForComponentResponse200.from_dict(
            response.json()
        )

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, GetDependencyGraphForComponentResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_uuid: UUID,
    component_uuids: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, GetDependencyGraphForComponentResponse200]]:
    """Returns the expanded dependency graph to every occurrence of a component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        project_uuid (UUID):
        component_uuids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetDependencyGraphForComponentResponse200]]
    """

    kwargs = _get_kwargs(
        project_uuid=project_uuid,
        component_uuids=component_uuids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_uuid: UUID,
    component_uuids: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, GetDependencyGraphForComponentResponse200]]:
    """Returns the expanded dependency graph to every occurrence of a component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        project_uuid (UUID):
        component_uuids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetDependencyGraphForComponentResponse200]
    """

    return sync_detailed(
        project_uuid=project_uuid,
        component_uuids=component_uuids,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_uuid: UUID,
    component_uuids: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, GetDependencyGraphForComponentResponse200]]:
    """Returns the expanded dependency graph to every occurrence of a component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        project_uuid (UUID):
        component_uuids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetDependencyGraphForComponentResponse200]]
    """

    kwargs = _get_kwargs(
        project_uuid=project_uuid,
        component_uuids=component_uuids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_uuid: UUID,
    component_uuids: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, GetDependencyGraphForComponentResponse200]]:
    """Returns the expanded dependency graph to every occurrence of a component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        project_uuid (UUID):
        component_uuids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetDependencyGraphForComponentResponse200]
    """

    return (
        await asyncio_detailed(
            project_uuid=project_uuid,
            component_uuids=component_uuids,
            client=client,
        )
    ).parsed
