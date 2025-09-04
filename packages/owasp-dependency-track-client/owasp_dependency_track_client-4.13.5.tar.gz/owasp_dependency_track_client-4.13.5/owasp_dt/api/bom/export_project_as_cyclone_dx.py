from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    uuid: UUID,
    *,
    format_: Union[Unset, str] = UNSET,
    variant: Union[Unset, str] = UNSET,
    download: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["format"] = format_

    params["variant"] = variant

    params["download"] = download

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/bom/cyclonedx/project/{uuid}".format(
            uuid=uuid,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, str]]:
    if response.status_code == 200:
        response_200 = cast(str, response.json())
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
) -> Response[Union[Any, str]]:
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
    format_: Union[Unset, str] = UNSET,
    variant: Union[Unset, str] = UNSET,
    download: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, str]]:
    """Returns dependency metadata for a project in CycloneDX format

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        format_ (Union[Unset, str]):
        variant (Union[Unset, str]):
        download (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        format_=format_,
        variant=variant,
        download=download,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = UNSET,
    variant: Union[Unset, str] = UNSET,
    download: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, str]]:
    """Returns dependency metadata for a project in CycloneDX format

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        format_ (Union[Unset, str]):
        variant (Union[Unset, str]):
        download (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, str]
    """

    return sync_detailed(
        uuid=uuid,
        client=client,
        format_=format_,
        variant=variant,
        download=download,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = UNSET,
    variant: Union[Unset, str] = UNSET,
    download: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, str]]:
    """Returns dependency metadata for a project in CycloneDX format

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        format_ (Union[Unset, str]):
        variant (Union[Unset, str]):
        download (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        format_=format_,
        variant=variant,
        download=download,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    *,
    client: AuthenticatedClient,
    format_: Union[Unset, str] = UNSET,
    variant: Union[Unset, str] = UNSET,
    download: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, str]]:
    """Returns dependency metadata for a project in CycloneDX format

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        format_ (Union[Unset, str]):
        variant (Union[Unset, str]):
        download (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, str]
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            client=client,
            format_=format_,
            variant=variant,
            download=download,
        )
    ).parsed
