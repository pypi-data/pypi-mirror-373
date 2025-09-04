from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.tag_operation_problem_details import TagOperationProblemDetails
from ...types import Response


def _get_kwargs(
    *,
    body: list[str],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/tag",
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, TagOperationProblemDetails]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 400:
        response_400 = TagOperationProblemDetails.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, TagOperationProblemDetails]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: list[str],
) -> Response[Union[Any, TagOperationProblemDetails]]:
    """Deletes one or more tags.

     <p>A tag can only be deleted if no projects or policies are assigned to it.</p>
    <p>
      Principals with <strong>PORTFOLIO_MANAGEMENT</strong> permission, and access
      to <em>all</em> assigned projects (if portfolio ACL is enabled), can delete
      a tag with assigned projects.
    </p>
    <p>
      Principals with <strong>POLICY_MANAGEMENT</strong> permission can delete tags
      with assigned policies.
    </p>
    <p>Requires permission <strong>TAG_MANAGEMENT</strong></p>

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TagOperationProblemDetails]]
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
    body: list[str],
) -> Optional[Union[Any, TagOperationProblemDetails]]:
    """Deletes one or more tags.

     <p>A tag can only be deleted if no projects or policies are assigned to it.</p>
    <p>
      Principals with <strong>PORTFOLIO_MANAGEMENT</strong> permission, and access
      to <em>all</em> assigned projects (if portfolio ACL is enabled), can delete
      a tag with assigned projects.
    </p>
    <p>
      Principals with <strong>POLICY_MANAGEMENT</strong> permission can delete tags
      with assigned policies.
    </p>
    <p>Requires permission <strong>TAG_MANAGEMENT</strong></p>

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TagOperationProblemDetails]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: list[str],
) -> Response[Union[Any, TagOperationProblemDetails]]:
    """Deletes one or more tags.

     <p>A tag can only be deleted if no projects or policies are assigned to it.</p>
    <p>
      Principals with <strong>PORTFOLIO_MANAGEMENT</strong> permission, and access
      to <em>all</em> assigned projects (if portfolio ACL is enabled), can delete
      a tag with assigned projects.
    </p>
    <p>
      Principals with <strong>POLICY_MANAGEMENT</strong> permission can delete tags
      with assigned policies.
    </p>
    <p>Requires permission <strong>TAG_MANAGEMENT</strong></p>

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TagOperationProblemDetails]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: list[str],
) -> Optional[Union[Any, TagOperationProblemDetails]]:
    """Deletes one or more tags.

     <p>A tag can only be deleted if no projects or policies are assigned to it.</p>
    <p>
      Principals with <strong>PORTFOLIO_MANAGEMENT</strong> permission, and access
      to <em>all</em> assigned projects (if portfolio ACL is enabled), can delete
      a tag with assigned projects.
    </p>
    <p>
      Principals with <strong>POLICY_MANAGEMENT</strong> permission can delete tags
      with assigned policies.
    </p>
    <p>Requires permission <strong>TAG_MANAGEMENT</strong></p>

    Args:
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TagOperationProblemDetails]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
