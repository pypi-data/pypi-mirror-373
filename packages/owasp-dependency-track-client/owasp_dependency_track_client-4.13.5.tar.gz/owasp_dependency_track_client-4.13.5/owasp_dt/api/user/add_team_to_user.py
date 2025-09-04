from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.identifiable_object import IdentifiableObject
from ...models.user_principal import UserPrincipal
from ...types import Response


def _get_kwargs(
    username: str,
    *,
    body: IdentifiableObject,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/user/{username}/membership".format(
            username=username,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, UserPrincipal]]:
    if response.status_code == 200:
        response_200 = UserPrincipal.from_dict(response.json())

        return response_200

    if response.status_code == 304:
        response_304 = cast(Any, None)
        return response_304

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
) -> Response[Union[Any, UserPrincipal]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    username: str,
    *,
    client: AuthenticatedClient,
    body: IdentifiableObject,
) -> Response[Union[Any, UserPrincipal]]:
    """Adds the username to the specified team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        username (str):
        body (IdentifiableObject):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UserPrincipal]]
    """

    kwargs = _get_kwargs(
        username=username,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    username: str,
    *,
    client: AuthenticatedClient,
    body: IdentifiableObject,
) -> Optional[Union[Any, UserPrincipal]]:
    """Adds the username to the specified team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        username (str):
        body (IdentifiableObject):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UserPrincipal]
    """

    return sync_detailed(
        username=username,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    username: str,
    *,
    client: AuthenticatedClient,
    body: IdentifiableObject,
) -> Response[Union[Any, UserPrincipal]]:
    """Adds the username to the specified team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        username (str):
        body (IdentifiableObject):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UserPrincipal]]
    """

    kwargs = _get_kwargs(
        username=username,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    username: str,
    *,
    client: AuthenticatedClient,
    body: IdentifiableObject,
) -> Optional[Union[Any, UserPrincipal]]:
    """Adds the username to the specified team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        username (str):
        body (IdentifiableObject):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UserPrincipal]
    """

    return (
        await asyncio_detailed(
            username=username,
            client=client,
            body=body,
        )
    ).parsed
