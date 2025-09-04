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
    project_uuid: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/policy/{policy_uuid}/project/{project_uuid}".format(
            policy_uuid=policy_uuid,
            project_uuid=project_uuid,
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
    project_uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, Policy]]:
    """Removes a project from a policy

     <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        project_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Policy]]
    """

    kwargs = _get_kwargs(
        policy_uuid=policy_uuid,
        project_uuid=project_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_uuid: UUID,
    project_uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, Policy]]:
    """Removes a project from a policy

     <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        project_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Policy]
    """

    return sync_detailed(
        policy_uuid=policy_uuid,
        project_uuid=project_uuid,
        client=client,
    ).parsed


async def asyncio_detailed(
    policy_uuid: UUID,
    project_uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, Policy]]:
    """Removes a project from a policy

     <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        project_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Policy]]
    """

    kwargs = _get_kwargs(
        policy_uuid=policy_uuid,
        project_uuid=project_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_uuid: UUID,
    project_uuid: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, Policy]]:
    """Removes a project from a policy

     <p>Requires permission <strong>POLICY_MANAGEMENT</strong></p>

    Args:
        policy_uuid (UUID):
        project_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Policy]
    """

    return (
        await asyncio_detailed(
            policy_uuid=policy_uuid,
            project_uuid=project_uuid,
            client=client,
        )
    ).parsed
