from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_projects_by_classifier_sort_order import (
    GetProjectsByClassifierSortOrder,
)
from ...models.project import Project
from ...types import UNSET, Response, Unset


def _get_kwargs(
    classifier: str,
    *,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetProjectsByClassifierSortOrder] = UNSET,
    exclude_inactive: Union[Unset, bool] = UNSET,
    only_root: Union[Unset, bool] = UNSET,
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

    params["excludeInactive"] = exclude_inactive

    params["onlyRoot"] = only_root

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/project/classifier/{classifier}".format(
            classifier=classifier,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["Project"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Project.from_dict(response_200_item_data)

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
) -> Response[Union[Any, list["Project"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    classifier: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetProjectsByClassifierSortOrder] = UNSET,
    exclude_inactive: Union[Unset, bool] = UNSET,
    only_root: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, list["Project"]]]:
    """Returns a list of all projects by classifier

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        classifier (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetProjectsByClassifierSortOrder]):
        exclude_inactive (Union[Unset, bool]):
        only_root (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Project']]]
    """

    kwargs = _get_kwargs(
        classifier=classifier,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        exclude_inactive=exclude_inactive,
        only_root=only_root,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    classifier: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetProjectsByClassifierSortOrder] = UNSET,
    exclude_inactive: Union[Unset, bool] = UNSET,
    only_root: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, list["Project"]]]:
    """Returns a list of all projects by classifier

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        classifier (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetProjectsByClassifierSortOrder]):
        exclude_inactive (Union[Unset, bool]):
        only_root (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Project']]
    """

    return sync_detailed(
        classifier=classifier,
        client=client,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        exclude_inactive=exclude_inactive,
        only_root=only_root,
    ).parsed


async def asyncio_detailed(
    classifier: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetProjectsByClassifierSortOrder] = UNSET,
    exclude_inactive: Union[Unset, bool] = UNSET,
    only_root: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, list["Project"]]]:
    """Returns a list of all projects by classifier

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        classifier (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetProjectsByClassifierSortOrder]):
        exclude_inactive (Union[Unset, bool]):
        only_root (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Project']]]
    """

    kwargs = _get_kwargs(
        classifier=classifier,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        exclude_inactive=exclude_inactive,
        only_root=only_root,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    classifier: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetProjectsByClassifierSortOrder] = UNSET,
    exclude_inactive: Union[Unset, bool] = UNSET,
    only_root: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, list["Project"]]]:
    """Returns a list of all projects by classifier

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        classifier (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetProjectsByClassifierSortOrder]):
        exclude_inactive (Union[Unset, bool]):
        only_root (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Project']]
    """

    return (
        await asyncio_detailed(
            classifier=classifier,
            client=client,
            page_number=page_number,
            page_size=page_size,
            offset=offset,
            limit=limit,
            sort_name=sort_name,
            sort_order=sort_order,
            exclude_inactive=exclude_inactive,
            only_root=only_root,
        )
    ).parsed
