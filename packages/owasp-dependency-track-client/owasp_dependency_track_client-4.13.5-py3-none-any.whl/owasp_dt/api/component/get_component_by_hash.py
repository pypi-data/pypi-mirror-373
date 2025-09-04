from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.component import Component
from ...models.get_component_by_hash_sort_order import GetComponentByHashSortOrder
from ...types import UNSET, Response, Unset


def _get_kwargs(
    hash_: str,
    *,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByHashSortOrder] = UNSET,
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
        "url": "/v1/component/hash/{hash_}".format(
            hash_=hash_,
        ),
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
    hash_: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByHashSortOrder] = UNSET,
) -> Response[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified hash value

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        hash_ (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByHashSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Component']]]
    """

    kwargs = _get_kwargs(
        hash_=hash_,
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
    hash_: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByHashSortOrder] = UNSET,
) -> Optional[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified hash value

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        hash_ (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByHashSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Component']]
    """

    return sync_detailed(
        hash_=hash_,
        client=client,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    hash_: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByHashSortOrder] = UNSET,
) -> Response[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified hash value

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        hash_ (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByHashSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Component']]]
    """

    kwargs = _get_kwargs(
        hash_=hash_,
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
    hash_: str,
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetComponentByHashSortOrder] = UNSET,
) -> Optional[Union[Any, list["Component"]]]:
    """Returns a list of components that have the specified hash value

     <p>Requires permission <strong>VIEW_PORTFOLIO</strong></p>

    Args:
        hash_ (str):
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetComponentByHashSortOrder]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Component']]
    """

    return (
        await asyncio_detailed(
            hash_=hash_,
            client=client,
            page_number=page_number,
            page_size=page_size,
            offset=offset,
            limit=limit,
            sort_name=sort_name,
            sort_order=sort_order,
        )
    ).parsed
