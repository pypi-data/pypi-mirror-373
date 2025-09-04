from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bom_upload_response import BomUploadResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    type_: Union[Unset, list[str]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_type_: Union[Unset, list[str]] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_

    params["type"] = json_type_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/search/reindex",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, BomUploadResponse]]:
    if response.status_code == 200:
        response_200 = BomUploadResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, BomUploadResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    type_: Union[Unset, list[str]] = UNSET,
) -> Response[Union[Any, BomUploadResponse]]:
    """Rebuild lucene indexes for search operations

     <p>Requires permission <strong>SYSTEM_CONFIGURATION</strong></p>

    Args:
        type_ (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BomUploadResponse]]
    """

    kwargs = _get_kwargs(
        type_=type_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    type_: Union[Unset, list[str]] = UNSET,
) -> Optional[Union[Any, BomUploadResponse]]:
    """Rebuild lucene indexes for search operations

     <p>Requires permission <strong>SYSTEM_CONFIGURATION</strong></p>

    Args:
        type_ (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BomUploadResponse]
    """

    return sync_detailed(
        client=client,
        type_=type_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    type_: Union[Unset, list[str]] = UNSET,
) -> Response[Union[Any, BomUploadResponse]]:
    """Rebuild lucene indexes for search operations

     <p>Requires permission <strong>SYSTEM_CONFIGURATION</strong></p>

    Args:
        type_ (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BomUploadResponse]]
    """

    kwargs = _get_kwargs(
        type_=type_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    type_: Union[Unset, list[str]] = UNSET,
) -> Optional[Union[Any, BomUploadResponse]]:
    """Rebuild lucene indexes for search operations

     <p>Requires permission <strong>SYSTEM_CONFIGURATION</strong></p>

    Args:
        type_ (Union[Unset, list[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BomUploadResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            type_=type_,
        )
    ).parsed
