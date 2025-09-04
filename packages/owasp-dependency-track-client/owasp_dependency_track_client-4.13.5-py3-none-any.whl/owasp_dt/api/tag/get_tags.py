from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_tags_sort_order import GetTagsSortOrder
from ...models.tag import Tag
from ...types import UNSET, Response, Unset


def _get_kwargs(
    policy_uuid: UUID,
    *,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetTagsSortOrder] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageNumber"] = page_number

    params["pageSize"] = page_size

    params["offset"] = offset

    params["limit"] = limit

    params["sortName"] = sort_name

    json_sort_order: Union[Unset, str] = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sortOrder"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/tag/{policy_uuid}".format(
            policy_uuid=policy_uuid,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["Tag"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Tag.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[Any, list["Tag"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy_uuid: UUID,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetTagsSortOrder] = UNSET,
) -> Response[Union[Any, list["Tag"]]]:
    """Returns a list of all tags associated with a given policy

     <p><strong>Deprecated</strong>. Use <code>/api/v1/tag/policy/{uuid}</code> instead.</p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        policy_uuid (UUID):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetTagsSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Tag']]]
    """

    kwargs = _get_kwargs(
        policy_uuid=policy_uuid,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_uuid: UUID,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetTagsSortOrder] = UNSET,
) -> Optional[Union[Any, list["Tag"]]]:
    """Returns a list of all tags associated with a given policy

     <p><strong>Deprecated</strong>. Use <code>/api/v1/tag/policy/{uuid}</code> instead.</p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        policy_uuid (UUID):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetTagsSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Tag']]
    """

    return sync_detailed(
        policy_uuid=policy_uuid,
        client=client,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    policy_uuid: UUID,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetTagsSortOrder] = UNSET,
) -> Response[Union[Any, list["Tag"]]]:
    """Returns a list of all tags associated with a given policy

     <p><strong>Deprecated</strong>. Use <code>/api/v1/tag/policy/{uuid}</code> instead.</p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        policy_uuid (UUID):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetTagsSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Tag']]]
    """

    kwargs = _get_kwargs(
        policy_uuid=policy_uuid,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_uuid: UUID,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetTagsSortOrder] = UNSET,
) -> Optional[Union[Any, list["Tag"]]]:
    """Returns a list of all tags associated with a given policy

     <p><strong>Deprecated</strong>. Use <code>/api/v1/tag/policy/{uuid}</code> instead.</p>
    <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        policy_uuid (UUID):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetTagsSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Tag']]
    """

    return (
        await asyncio_detailed(
            policy_uuid=policy_uuid,
            client=client,
            page_number=page_number,
            page_size=page_size,
            offset=offset,
            limit=limit,
            sort_name=sort_name,
            sort_order=sort_order,
        )
    ).parsed
