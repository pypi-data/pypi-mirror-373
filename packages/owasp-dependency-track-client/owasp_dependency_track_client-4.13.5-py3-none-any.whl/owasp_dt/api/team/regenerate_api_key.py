from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_key import ApiKey
from ...types import Response


def _get_kwargs(
    public_id_or_key: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/team/key/{public_id_or_key}".format(
            public_id_or_key=public_id_or_key,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ApiKey]]:
    if response.status_code == 200:
        response_200 = ApiKey.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ApiKey]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    public_id_or_key: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, ApiKey]]:
    """Regenerates an API key by removing the specified key, generating a new one and returning its value

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        public_id_or_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ApiKey]]
    """

    kwargs = _get_kwargs(
        public_id_or_key=public_id_or_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    public_id_or_key: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, ApiKey]]:
    """Regenerates an API key by removing the specified key, generating a new one and returning its value

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        public_id_or_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ApiKey]
    """

    return sync_detailed(
        public_id_or_key=public_id_or_key,
        client=client,
    ).parsed


async def asyncio_detailed(
    public_id_or_key: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, ApiKey]]:
    """Regenerates an API key by removing the specified key, generating a new one and returning its value

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        public_id_or_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ApiKey]]
    """

    kwargs = _get_kwargs(
        public_id_or_key=public_id_or_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    public_id_or_key: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, ApiKey]]:
    """Regenerates an API key by removing the specified key, generating a new one and returning its value

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        public_id_or_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ApiKey]
    """

    return (
        await asyncio_detailed(
            public_id_or_key=public_id_or_key,
            client=client,
        )
    ).parsed
