from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project import Project
from ...types import UNSET, Response


def _get_kwargs(
    *,
    name: str,
    version: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["name"] = name

    params["version"] = version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/project/lookup",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Project]]:
    if response.status_code == 200:
        response_200 = Project.from_dict(response.json())

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
) -> Response[Union[Any, Project]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    version: str,
) -> Response[Union[Any, Project]]:
    """Returns a specific project by its name and version

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        name (str):
        version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Project]]
    """

    kwargs = _get_kwargs(
        name=name,
        version=version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
    version: str,
) -> Optional[Union[Any, Project]]:
    """Returns a specific project by its name and version

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        name (str):
        version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Project]
    """

    return sync_detailed(
        client=client,
        name=name,
        version=version,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    version: str,
) -> Response[Union[Any, Project]]:
    """Returns a specific project by its name and version

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        name (str):
        version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Project]]
    """

    kwargs = _get_kwargs(
        name=name,
        version=version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: str,
    version: str,
) -> Optional[Union[Any, Project]]:
    """Returns a specific project by its name and version

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        name (str):
        version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Project]
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            version=version,
        )
    ).parsed
