from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.score import Score
from ...types import UNSET, Response


def _get_kwargs(
    *,
    vector: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["vector"] = vector

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/calculator/owasp",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Score]]:
    if response.status_code == 200:
        response_200 = Score.from_dict(response.json())

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
) -> Response[Union[Any, Score]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    vector: str,
) -> Response[Union[Any, Score]]:
    """Returns the OWASP Risk Rating likelihood score, technical impact score and business impact score

    Args:
        vector (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Score]]
    """

    kwargs = _get_kwargs(
        vector=vector,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    vector: str,
) -> Optional[Union[Any, Score]]:
    """Returns the OWASP Risk Rating likelihood score, technical impact score and business impact score

    Args:
        vector (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Score]
    """

    return sync_detailed(
        client=client,
        vector=vector,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    vector: str,
) -> Response[Union[Any, Score]]:
    """Returns the OWASP Risk Rating likelihood score, technical impact score and business impact score

    Args:
        vector (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Score]]
    """

    kwargs = _get_kwargs(
        vector=vector,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    vector: str,
) -> Optional[Union[Any, Score]]:
    """Returns the OWASP Risk Rating likelihood score, technical impact score and business impact score

    Args:
        vector (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Score]
    """

    return (
        await asyncio_detailed(
            client=client,
            vector=vector,
        )
    ).parsed
