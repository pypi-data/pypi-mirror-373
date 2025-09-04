from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.component import Component
from ...models.get_component_by_identity_sort_order import (
    GetComponentByIdentitySortOrder,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByIdentitySortOrder] = UNSET,
    group: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    version: Union[Unset, str] = UNSET,
    purl: Union[Unset, str] = UNSET,
    cpe: Union[Unset, str] = UNSET,
    swid_tag_id: Union[Unset, str] = UNSET,
    project: Union[Unset, UUID] = UNSET,
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

    params["group"] = group

    params["name"] = name

    params["version"] = version

    params["purl"] = purl

    params["cpe"] = cpe

    params["swidTagId"] = swid_tag_id

    json_project: Union[Unset, str] = UNSET
    if not isinstance(project, Unset):
        json_project = str(project)
    params["project"] = json_project

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/component/identity",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["Component"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Component.from_dict(response_200_item_data)

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
) -> Response[Union[Any, list["Component"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByIdentitySortOrder] = UNSET,
    group: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    version: Union[Unset, str] = UNSET,
    purl: Union[Unset, str] = UNSET,
    cpe: Union[Unset, str] = UNSET,
    swid_tag_id: Union[Unset, str] = UNSET,
    project: Union[Unset, UUID] = UNSET,
) -> Response[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified component identity. This resource accepts
    coordinates (group, name, version) or purl, cpe, or swidTagId

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByIdentitySortOrder]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        purl (Union[Unset, str]):
        cpe (Union[Unset, str]):
        swid_tag_id (Union[Unset, str]):
        project (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Component']]]
    """

    kwargs = _get_kwargs(
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        group=group,
        name=name,
        version=version,
        purl=purl,
        cpe=cpe,
        swid_tag_id=swid_tag_id,
        project=project,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByIdentitySortOrder] = UNSET,
    group: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    version: Union[Unset, str] = UNSET,
    purl: Union[Unset, str] = UNSET,
    cpe: Union[Unset, str] = UNSET,
    swid_tag_id: Union[Unset, str] = UNSET,
    project: Union[Unset, UUID] = UNSET,
) -> Optional[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified component identity. This resource accepts
    coordinates (group, name, version) or purl, cpe, or swidTagId

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByIdentitySortOrder]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        purl (Union[Unset, str]):
        cpe (Union[Unset, str]):
        swid_tag_id (Union[Unset, str]):
        project (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Component']]
    """

    return sync_detailed(
        client=client,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        group=group,
        name=name,
        version=version,
        purl=purl,
        cpe=cpe,
        swid_tag_id=swid_tag_id,
        project=project,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByIdentitySortOrder] = UNSET,
    group: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    version: Union[Unset, str] = UNSET,
    purl: Union[Unset, str] = UNSET,
    cpe: Union[Unset, str] = UNSET,
    swid_tag_id: Union[Unset, str] = UNSET,
    project: Union[Unset, UUID] = UNSET,
) -> Response[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified component identity. This resource accepts
    coordinates (group, name, version) or purl, cpe, or swidTagId

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByIdentitySortOrder]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        purl (Union[Unset, str]):
        cpe (Union[Unset, str]):
        swid_tag_id (Union[Unset, str]):
        project (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Component']]]
    """

    kwargs = _get_kwargs(
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        group=group,
        name=name,
        version=version,
        purl=purl,
        cpe=cpe,
        swid_tag_id=swid_tag_id,
        project=project,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByIdentitySortOrder] = UNSET,
    group: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    version: Union[Unset, str] = UNSET,
    purl: Union[Unset, str] = UNSET,
    cpe: Union[Unset, str] = UNSET,
    swid_tag_id: Union[Unset, str] = UNSET,
    project: Union[Unset, UUID] = UNSET,
) -> Optional[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified component identity. This resource accepts
    coordinates (group, name, version) or purl, cpe, or swidTagId

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByIdentitySortOrder]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        purl (Union[Unset, str]):
        cpe (Union[Unset, str]):
        swid_tag_id (Union[Unset, str]):
        project (Union[Unset, UUID]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Component']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page_number=page_number,
            page_size=page_size,
            offset=offset,
            limit=limit,
            sort_name=sort_name,
            sort_order=sort_order,
            group=group,
            name=name,
            version=version,
            purl=purl,
            cpe=cpe,
            swid_tag_id=swid_tag_id,
            project=project,
        )
    ).parsed
