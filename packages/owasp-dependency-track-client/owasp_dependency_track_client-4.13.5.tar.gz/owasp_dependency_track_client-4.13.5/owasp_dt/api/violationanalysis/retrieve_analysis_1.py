from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.violation_analysis import ViolationAnalysis
from ...types import UNSET, Response


def _get_kwargs(
    *,
    component: UUID,
    policy_violation: UUID,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_component = str(component)
    params["component"] = json_component

    json_policy_violation = str(policy_violation)
    params["policyViolation"] = json_policy_violation

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/violation/analysis",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ViolationAnalysis]]:
    if response.status_code == 200:
        response_200 = ViolationAnalysis.from_dict(response.json())

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
) -> Response[Union[Any, ViolationAnalysis]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    component: UUID,
    policy_violation: UUID,
) -> Response[Union[Any, ViolationAnalysis]]:
    """Retrieves a violation analysis trail

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        component (UUID):
        policy_violation (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ViolationAnalysis]]
    """

    kwargs = _get_kwargs(
        component=component,
        policy_violation=policy_violation,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    component: UUID,
    policy_violation: UUID,
) -> Optional[Union[Any, ViolationAnalysis]]:
    """Retrieves a violation analysis trail

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        component (UUID):
        policy_violation (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ViolationAnalysis]
    """

    return sync_detailed(
        client=client,
        component=component,
        policy_violation=policy_violation,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    component: UUID,
    policy_violation: UUID,
) -> Response[Union[Any, ViolationAnalysis]]:
    """Retrieves a violation analysis trail

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        component (UUID):
        policy_violation (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ViolationAnalysis]]
    """

    kwargs = _get_kwargs(
        component=component,
        policy_violation=policy_violation,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    component: UUID,
    policy_violation: UUID,
) -> Optional[Union[Any, ViolationAnalysis]]:
    """Retrieves a violation analysis trail

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        component (UUID):
        policy_violation (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ViolationAnalysis]
    """

    return (
        await asyncio_detailed(
            client=client,
            component=component,
            policy_violation=policy_violation,
        )
    ).parsed
