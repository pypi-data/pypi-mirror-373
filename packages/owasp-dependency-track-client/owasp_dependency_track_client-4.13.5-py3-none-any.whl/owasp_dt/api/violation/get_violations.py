from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_violations_sort_order import GetViolationsSortOrder
from ...models.policy_violation import PolicyViolation
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetViolationsSortOrder] = UNSET,
    suppressed: Union[Unset, bool] = UNSET,
    show_inactive: Union[Unset, bool] = UNSET,
    violation_state: Union[Unset, str] = UNSET,
    risk_type: Union[Unset, str] = UNSET,
    policy: Union[Unset, str] = UNSET,
    analysis_state: Union[Unset, str] = UNSET,
    occurred_on_date_from: Union[Unset, str] = UNSET,
    occurred_on_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
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

    params["suppressed"] = suppressed

    params["showInactive"] = show_inactive

    params["violationState"] = violation_state

    params["riskType"] = risk_type

    params["policy"] = policy

    params["analysisState"] = analysis_state

    params["occurredOnDateFrom"] = occurred_on_date_from

    params["occurredOnDateTo"] = occurred_on_date_to

    params["textSearchField"] = text_search_field

    params["textSearchInput"] = text_search_input

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/violation",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["PolicyViolation"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PolicyViolation.from_dict(response_200_item_data)

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
) -> Response[Union[Any, list["PolicyViolation"]]]:
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
    sort_order: Union[Unset, GetViolationsSortOrder] = UNSET,
    suppressed: Union[Unset, bool] = UNSET,
    show_inactive: Union[Unset, bool] = UNSET,
    violation_state: Union[Unset, str] = UNSET,
    risk_type: Union[Unset, str] = UNSET,
    policy: Union[Unset, str] = UNSET,
    analysis_state: Union[Unset, str] = UNSET,
    occurred_on_date_from: Union[Unset, str] = UNSET,
    occurred_on_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
) -> Response[Union[Any, list["PolicyViolation"]]]:
    """Returns a list of all policy violations for the entire portfolio

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetViolationsSortOrder]):
        suppressed (Union[Unset, bool]):
        show_inactive (Union[Unset, bool]):
        violation_state (Union[Unset, str]):
        risk_type (Union[Unset, str]):
        policy (Union[Unset, str]):
        analysis_state (Union[Unset, str]):
        occurred_on_date_from (Union[Unset, str]):
        occurred_on_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['PolicyViolation']]]
    """

    kwargs = _get_kwargs(
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        suppressed=suppressed,
        show_inactive=show_inactive,
        violation_state=violation_state,
        risk_type=risk_type,
        policy=policy,
        analysis_state=analysis_state,
        occurred_on_date_from=occurred_on_date_from,
        occurred_on_date_to=occurred_on_date_to,
        text_search_field=text_search_field,
        text_search_input=text_search_input,
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
    sort_order: Union[Unset, GetViolationsSortOrder] = UNSET,
    suppressed: Union[Unset, bool] = UNSET,
    show_inactive: Union[Unset, bool] = UNSET,
    violation_state: Union[Unset, str] = UNSET,
    risk_type: Union[Unset, str] = UNSET,
    policy: Union[Unset, str] = UNSET,
    analysis_state: Union[Unset, str] = UNSET,
    occurred_on_date_from: Union[Unset, str] = UNSET,
    occurred_on_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, list["PolicyViolation"]]]:
    """Returns a list of all policy violations for the entire portfolio

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetViolationsSortOrder]):
        suppressed (Union[Unset, bool]):
        show_inactive (Union[Unset, bool]):
        violation_state (Union[Unset, str]):
        risk_type (Union[Unset, str]):
        policy (Union[Unset, str]):
        analysis_state (Union[Unset, str]):
        occurred_on_date_from (Union[Unset, str]):
        occurred_on_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['PolicyViolation']]
    """

    return sync_detailed(
        client=client,
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        suppressed=suppressed,
        show_inactive=show_inactive,
        violation_state=violation_state,
        risk_type=risk_type,
        policy=policy,
        analysis_state=analysis_state,
        occurred_on_date_from=occurred_on_date_from,
        occurred_on_date_to=occurred_on_date_to,
        text_search_field=text_search_field,
        text_search_input=text_search_input,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, str] = "1",
    page_size: Union[Unset, str] = "100",
    offset: Union[Unset, str] = UNSET,
    limit: Union[Unset, str] = UNSET,
    sort_name: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, GetViolationsSortOrder] = UNSET,
    suppressed: Union[Unset, bool] = UNSET,
    show_inactive: Union[Unset, bool] = UNSET,
    violation_state: Union[Unset, str] = UNSET,
    risk_type: Union[Unset, str] = UNSET,
    policy: Union[Unset, str] = UNSET,
    analysis_state: Union[Unset, str] = UNSET,
    occurred_on_date_from: Union[Unset, str] = UNSET,
    occurred_on_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
) -> Response[Union[Any, list["PolicyViolation"]]]:
    """Returns a list of all policy violations for the entire portfolio

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetViolationsSortOrder]):
        suppressed (Union[Unset, bool]):
        show_inactive (Union[Unset, bool]):
        violation_state (Union[Unset, str]):
        risk_type (Union[Unset, str]):
        policy (Union[Unset, str]):
        analysis_state (Union[Unset, str]):
        occurred_on_date_from (Union[Unset, str]):
        occurred_on_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['PolicyViolation']]]
    """

    kwargs = _get_kwargs(
        page_number=page_number,
        page_size=page_size,
        offset=offset,
        limit=limit,
        sort_name=sort_name,
        sort_order=sort_order,
        suppressed=suppressed,
        show_inactive=show_inactive,
        violation_state=violation_state,
        risk_type=risk_type,
        policy=policy,
        analysis_state=analysis_state,
        occurred_on_date_from=occurred_on_date_from,
        occurred_on_date_to=occurred_on_date_to,
        text_search_field=text_search_field,
        text_search_input=text_search_input,
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
    sort_order: Union[Unset, GetViolationsSortOrder] = UNSET,
    suppressed: Union[Unset, bool] = UNSET,
    show_inactive: Union[Unset, bool] = UNSET,
    violation_state: Union[Unset, str] = UNSET,
    risk_type: Union[Unset, str] = UNSET,
    policy: Union[Unset, str] = UNSET,
    analysis_state: Union[Unset, str] = UNSET,
    occurred_on_date_from: Union[Unset, str] = UNSET,
    occurred_on_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, list["PolicyViolation"]]]:
    """Returns a list of all policy violations for the entire portfolio

     <p>Requires permission <strong>VIEW_POLICY_VIOLATION</strong></p>

    Args:
        page_number (Union[Unset, str]):  Default: '1'.
        page_size (Union[Unset, str]):  Default: '100'.
        offset (Union[Unset, str]):
        limit (Union[Unset, str]):
        sort_name (Union[Unset, str]):
        sort_order (Union[Unset, GetViolationsSortOrder]):
        suppressed (Union[Unset, bool]):
        show_inactive (Union[Unset, bool]):
        violation_state (Union[Unset, str]):
        risk_type (Union[Unset, str]):
        policy (Union[Unset, str]):
        analysis_state (Union[Unset, str]):
        occurred_on_date_from (Union[Unset, str]):
        occurred_on_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['PolicyViolation']]
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
            suppressed=suppressed,
            show_inactive=show_inactive,
            violation_state=violation_state,
            risk_type=risk_type,
            policy=policy,
            analysis_state=analysis_state,
            occurred_on_date_from=occurred_on_date_from,
            occurred_on_date_to=occurred_on_date_to,
            text_search_field=text_search_field,
            text_search_input=text_search_input,
        )
    ).parsed
