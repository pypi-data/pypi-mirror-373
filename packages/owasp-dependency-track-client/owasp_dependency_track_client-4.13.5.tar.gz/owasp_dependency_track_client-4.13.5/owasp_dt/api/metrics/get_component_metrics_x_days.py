from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dependency_metrics import DependencyMetrics
from ...types import Response


def _get_kwargs(
    uuid: UUID,
    days: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/metrics/component/{uuid}/days/{days}".format(
            uuid=uuid,
            days=days,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["DependencyMetrics"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DependencyMetrics.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[Any, list["DependencyMetrics"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uuid: UUID,
    days: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, list["DependencyMetrics"]]]:
    """Returns X days of historical metrics for a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['DependencyMetrics']]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        days=days,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    days: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, list["DependencyMetrics"]]]:
    """Returns X days of historical metrics for a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['DependencyMetrics']]
    """

    return sync_detailed(
        uuid=uuid,
        days=days,
        client=client,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    days: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, list["DependencyMetrics"]]]:
    """Returns X days of historical metrics for a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['DependencyMetrics']]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        days=days,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    days: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, list["DependencyMetrics"]]]:
    """Returns X days of historical metrics for a specific component

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['DependencyMetrics']]
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            days=days,
            client=client,
        )
    ).parsed
