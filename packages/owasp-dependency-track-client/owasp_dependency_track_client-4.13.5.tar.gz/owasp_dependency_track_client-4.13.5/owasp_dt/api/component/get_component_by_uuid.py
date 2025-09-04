from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.component import Component
from ...types import UNSET, Response, Unset


def _get_kwargs(
    uuid: UUID,
    *,
    include_repository_meta_data: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["includeRepositoryMetaData"] = include_repository_meta_data

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/component/{uuid}".format(
            uuid=uuid,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Component]]:
    if response.status_code == 200:
        response_200 = Component.from_dict(response.json())

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
) -> Response[Union[Any, Component]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    include_repository_meta_data: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, Component]]:
    """Returns a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        include_repository_meta_data (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Component]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        include_repository_meta_data=include_repository_meta_data,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    include_repository_meta_data: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, Component]]:
    """Returns a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        include_repository_meta_data (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Component]
    """

    return sync_detailed(
        uuid=uuid,
        client=client,
        include_repository_meta_data=include_repository_meta_data,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    include_repository_meta_data: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, Component]]:
    """Returns a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        include_repository_meta_data (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Component]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        include_repository_meta_data=include_repository_meta_data,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    include_repository_meta_data: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, Component]]:
    """Returns a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        include_repository_meta_data (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Component]
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            include_repository_meta_data=include_repository_meta_data,
        )
    ).parsed
