from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.portfolio_metrics import PortfolioMetrics
from ...types import Response


def _get_kwargs(
    days: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/metrics/portfolio/{days}/days".format(
            days=days,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["PortfolioMetrics"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PortfolioMetrics.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, list["PortfolioMetrics"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    days: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, list["PortfolioMetrics"]]]:
    """Returns X days of historical metrics for the entire portfolio

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['PortfolioMetrics']]]
    """

    kwargs = _get_kwargs(
        days=days,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    days: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, list["PortfolioMetrics"]]]:
    """Returns X days of historical metrics for the entire portfolio

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['PortfolioMetrics']]
    """

    return sync_detailed(
        days=days,
        client=client,
    ).parsed


async def asyncio_detailed(
    days: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, list["PortfolioMetrics"]]]:
    """Returns X days of historical metrics for the entire portfolio

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['PortfolioMetrics']]]
    """

    kwargs = _get_kwargs(
        days=days,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    days: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, list["PortfolioMetrics"]]]:
    """Returns X days of historical metrics for the entire portfolio

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        days (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['PortfolioMetrics']]
    """

    return (
        await asyncio_detailed(
            days=days,
            client=client,
        )
    ).parsed
