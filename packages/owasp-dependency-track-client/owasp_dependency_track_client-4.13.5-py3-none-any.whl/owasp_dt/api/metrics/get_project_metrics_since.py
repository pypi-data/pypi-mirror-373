from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_metrics import ProjectMetrics
from ...types import Response


def _get_kwargs(
    uuid: UUID,
    date: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/metrics/project/{uuid}/since/{date}".format(
            uuid=uuid,
            date=date,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["ProjectMetrics"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProjectMetrics.from_dict(response_200_item_data)

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
) -> Response[Union[Any, list["ProjectMetrics"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uuid: UUID,
    date: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, list["ProjectMetrics"]]]:
    """Returns historical metrics for a specific project from a specific date

     <p>Date format must be <code>YYYYMMDD</code></p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['ProjectMetrics']]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        date=date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uuid: UUID,
    date: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, list["ProjectMetrics"]]]:
    """Returns historical metrics for a specific project from a specific date

     <p>Date format must be <code>YYYYMMDD</code></p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['ProjectMetrics']]
    """

    return sync_detailed(
        uuid=uuid,
        date=date,
        client=client,
    ).parsed


async def asyncio_detailed(
    uuid: UUID,
    date: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, list["ProjectMetrics"]]]:
    """Returns historical metrics for a specific project from a specific date

     <p>Date format must be <code>YYYYMMDD</code></p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['ProjectMetrics']]]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        date=date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uuid: UUID,
    date: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, list["ProjectMetrics"]]]:
    """Returns historical metrics for a specific project from a specific date

     <p>Date format must be <code>YYYYMMDD</code></p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        uuid (UUID):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['ProjectMetrics']]
    """

    return (
        await asyncio_detailed(
            uuid=uuid,
            date=date,
            client=client,
        )
    ).parsed
