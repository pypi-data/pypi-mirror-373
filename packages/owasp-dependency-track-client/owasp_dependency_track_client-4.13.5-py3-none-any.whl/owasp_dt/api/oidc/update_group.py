from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oidc_group import OidcGroup
from ...types import Response


def _get_kwargs(
    *,
    body: OidcGroup,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/oidc/group",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, OidcGroup]]:
    if response.status_code == 200:
        response_200 = OidcGroup.from_dict(response.json())

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
) -> Response[Union[Any, OidcGroup]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: OidcGroup,
) -> Response[Union[Any, OidcGroup]]:
    """Updates group

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        body (OidcGroup):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, OidcGroup]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: OidcGroup,
) -> Optional[Union[Any, OidcGroup]]:
    """Updates group

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        body (OidcGroup):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, OidcGroup]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: OidcGroup,
) -> Response[Union[Any, OidcGroup]]:
    """Updates group

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        body (OidcGroup):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, OidcGroup]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: OidcGroup,
) -> Optional[Union[Any, OidcGroup]]:
    """Updates group

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        body (OidcGroup):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, OidcGroup]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
