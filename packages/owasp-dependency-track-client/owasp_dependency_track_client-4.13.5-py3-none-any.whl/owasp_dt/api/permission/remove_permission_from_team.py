from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.team import Team
from ...types import Response


def _get_kwargs(
    permission: str,
    uuid: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/permission/{permission}/team/{uuid}".format(
            permission=permission,
            uuid=uuid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Team]]:
    if response.status_code == 200:
        response_200 = Team.from_dict(response.json())

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
) -> Response[Union[Any, Team]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    permission: str,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, Team]]:
    """Removes the permission from the team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        permission (str):
        uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Team]]
    """

    kwargs = _get_kwargs(
        permission=permission,
        uuid=uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    permission: str,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, Team]]:
    """Removes the permission from the team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        permission (str):
        uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Team]
    """

    return sync_detailed(
        permission=permission,
        uuid=uuid,
        client=client,
    ).parsed


async def asyncio_detailed(
    permission: str,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, Team]]:
    """Removes the permission from the team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        permission (str):
        uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Team]]
    """

    kwargs = _get_kwargs(
        permission=permission,
        uuid=uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    permission: str,
    uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, Team]]:
    """Removes the permission from the team.

     <p>Requires permission <strong>ACCESS_MANAGEMENT</strong></p>

    Args:
        permission (str):
        uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Team]
    """

    return (
        await asyncio_detailed(
            permission=permission,
            uuid=uuid,
            client=client,
        )
    ).parsed
