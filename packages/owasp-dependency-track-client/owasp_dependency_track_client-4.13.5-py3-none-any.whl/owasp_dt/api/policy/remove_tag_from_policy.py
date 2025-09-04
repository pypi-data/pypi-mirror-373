from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.policy import Policy
from ...types import Response


def _get_kwargs(
    policy_uuid: UUID,
    tag_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/policy/{policy_uuid}/tag/{tag_name}".format(
            policy_uuid=policy_uuid,
            tag_name=tag_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Policy]]:
    if response.status_code == 200:
        response_200 = Policy.from_dict(response.json())

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
) -> Response[Union[Any, Policy]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy_uuid: UUID,
    tag_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, Policy]]:
    """Removes a tag from a policy

     <p><strong>Deprecated</strong>. Use <code>DELETE /api/v1/tag/{name}/policy</code> instead.</p>
    <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        tag_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Policy]]
    """

    kwargs = _get_kwargs(
        policy_uuid=policy_uuid,
        tag_name=tag_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_uuid: UUID,
    tag_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, Policy]]:
    """Removes a tag from a policy

     <p><strong>Deprecated</strong>. Use <code>DELETE /api/v1/tag/{name}/policy</code> instead.</p>
    <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        tag_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Policy]
    """

    return sync_detailed(
        policy_uuid=policy_uuid,
        tag_name=tag_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    policy_uuid: UUID,
    tag_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, Policy]]:
    """Removes a tag from a policy

     <p><strong>Deprecated</strong>. Use <code>DELETE /api/v1/tag/{name}/policy</code> instead.</p>
    <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        tag_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Policy]]
    """

    kwargs = _get_kwargs(
        policy_uuid=policy_uuid,
        tag_name=tag_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_uuid: UUID,
    tag_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, Policy]]:
    """Removes a tag from a policy

     <p><strong>Deprecated</strong>. Use <code>DELETE /api/v1/tag/{name}/policy</code> instead.</p>
    <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        tag_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Policy]
    """

    return (
        await asyncio_detailed(
            policy_uuid=policy_uuid,
            tag_name=tag_name,
            client=client,
        )
    ).parsed
