from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project import Project
from ...types import Response


def _get_kwargs(
    *,
    body: Project,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/project",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Project]]:
    if response.status_code == 201:
        response_201 = Project.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 409:
        response_409 = cast(Any, None)
        return response_409

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, Project]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Project,
) -> Response[Union[Any, Project]]:
    """Creates a new project

     <p>If a parent project exists, <code>parent.uuid</code> is required</p>
    <p>
      When portfolio access control is enabled, one or more teams to grant access
      to can be provided via <code>accessTeams</code>. Either <code>uuid</code> or
      <code>name</code> of a team must be specified. Only teams which the authenticated
      principal is a member of can be assigned. Principals with <strong>ACCESS_MANAGEMENT</strong>
      permission can assign <em>any</em> team.
    </p>
    <p>Requires permission <strong>PORTFOLIO_MANAGEMENT</strong></p>

    Args:
        body (Project):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Project]]
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
    body: Project,
) -> Optional[Union[Any, Project]]:
    """Creates a new project

     <p>If a parent project exists, <code>parent.uuid</code> is required</p>
    <p>
      When portfolio access control is enabled, one or more teams to grant access
      to can be provided via <code>accessTeams</code>. Either <code>uuid</code> or
      <code>name</code> of a team must be specified. Only teams which the authenticated
      principal is a member of can be assigned. Principals with <strong>ACCESS_MANAGEMENT</strong>
      permission can assign <em>any</em> team.
    </p>
    <p>Requires permission <strong>PORTFOLIO_MANAGEMENT</strong></p>

    Args:
        body (Project):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Project]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Project,
) -> Response[Union[Any, Project]]:
    """Creates a new project

     <p>If a parent project exists, <code>parent.uuid</code> is required</p>
    <p>
      When portfolio access control is enabled, one or more teams to grant access
      to can be provided via <code>accessTeams</code>. Either <code>uuid</code> or
      <code>name</code> of a team must be specified. Only teams which the authenticated
      principal is a member of can be assigned. Principals with <strong>ACCESS_MANAGEMENT</strong>
      permission can assign <em>any</em> team.
    </p>
    <p>Requires permission <strong>PORTFOLIO_MANAGEMENT</strong></p>

    Args:
        body (Project):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Project]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Project,
) -> Optional[Union[Any, Project]]:
    """Creates a new project

     <p>If a parent project exists, <code>parent.uuid</code> is required</p>
    <p>
      When portfolio access control is enabled, one or more teams to grant access
      to can be provided via <code>accessTeams</code>. Either <code>uuid</code> or
      <code>name</code> of a team must be specified. Only teams which the authenticated
      principal is a member of can be assigned. Principals with <strong>ACCESS_MANAGEMENT</strong>
      permission can assign <em>any</em> team.
    </p>
    <p>Requires permission <strong>PORTFOLIO_MANAGEMENT</strong></p>

    Args:
        body (Project):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Project]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
