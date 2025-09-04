from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.finding import Finding
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    show_inactive: Union[Unset, bool] = UNSET,
    severity: Union[Unset, str] = UNSET,
    publish_date_from: Union[Unset, str] = UNSET,
    publish_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
    cvssv_2_from: Union[Unset, str] = UNSET,
    cvssv_2_to: Union[Unset, str] = UNSET,
    cvssv_3_from: Union[Unset, str] = UNSET,
    cvssv_3_to: Union[Unset, str] = UNSET,
    occurrences_from: Union[Unset, str] = UNSET,
    occurrences_to: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["showInactive"] = show_inactive

    params["severity"] = severity

    params["publishDateFrom"] = publish_date_from

    params["publishDateTo"] = publish_date_to

    params["textSearchField"] = text_search_field

    params["textSearchInput"] = text_search_input

    params["cvssv2From"] = cvssv_2_from

    params["cvssv2To"] = cvssv_2_to

    params["cvssv3From"] = cvssv_3_from

    params["cvssv3To"] = cvssv_3_to

    params["occurrencesFrom"] = occurrences_from

    params["occurrencesTo"] = occurrences_to

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/finding/grouped",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["Finding"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Finding.from_dict(response_200_item_data)

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
) -> Response[Union[Any, list["Finding"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    show_inactive: Union[Unset, bool] = UNSET,
    severity: Union[Unset, str] = UNSET,
    publish_date_from: Union[Unset, str] = UNSET,
    publish_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
    cvssv_2_from: Union[Unset, str] = UNSET,
    cvssv_2_to: Union[Unset, str] = UNSET,
    cvssv_3_from: Union[Unset, str] = UNSET,
    cvssv_3_to: Union[Unset, str] = UNSET,
    occurrences_from: Union[Unset, str] = UNSET,
    occurrences_to: Union[Unset, str] = UNSET,
) -> Response[Union[Any, list["Finding"]]]:
    """Returns a list of all findings grouped by vulnerability

     <p>Requires permission <strong>VIEW_VULNERABILITY</strong></p>

    Args:
        show_inactive (Union[Unset, bool]):
        severity (Union[Unset, str]):
        publish_date_from (Union[Unset, str]):
        publish_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):
        cvssv_2_from (Union[Unset, str]):
        cvssv_2_to (Union[Unset, str]):
        cvssv_3_from (Union[Unset, str]):
        cvssv_3_to (Union[Unset, str]):
        occurrences_from (Union[Unset, str]):
        occurrences_to (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Finding']]]
    """

    kwargs = _get_kwargs(
        show_inactive=show_inactive,
        severity=severity,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        text_search_field=text_search_field,
        text_search_input=text_search_input,
        cvssv_2_from=cvssv_2_from,
        cvssv_2_to=cvssv_2_to,
        cvssv_3_from=cvssv_3_from,
        cvssv_3_to=cvssv_3_to,
        occurrences_from=occurrences_from,
        occurrences_to=occurrences_to,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    show_inactive: Union[Unset, bool] = UNSET,
    severity: Union[Unset, str] = UNSET,
    publish_date_from: Union[Unset, str] = UNSET,
    publish_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
    cvssv_2_from: Union[Unset, str] = UNSET,
    cvssv_2_to: Union[Unset, str] = UNSET,
    cvssv_3_from: Union[Unset, str] = UNSET,
    cvssv_3_to: Union[Unset, str] = UNSET,
    occurrences_from: Union[Unset, str] = UNSET,
    occurrences_to: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, list["Finding"]]]:
    """Returns a list of all findings grouped by vulnerability

     <p>Requires permission <strong>VIEW_VULNERABILITY</strong></p>

    Args:
        show_inactive (Union[Unset, bool]):
        severity (Union[Unset, str]):
        publish_date_from (Union[Unset, str]):
        publish_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):
        cvssv_2_from (Union[Unset, str]):
        cvssv_2_to (Union[Unset, str]):
        cvssv_3_from (Union[Unset, str]):
        cvssv_3_to (Union[Unset, str]):
        occurrences_from (Union[Unset, str]):
        occurrences_to (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Finding']]
    """

    return sync_detailed(
        client=client,
        show_inactive=show_inactive,
        severity=severity,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        text_search_field=text_search_field,
        text_search_input=text_search_input,
        cvssv_2_from=cvssv_2_from,
        cvssv_2_to=cvssv_2_to,
        cvssv_3_from=cvssv_3_from,
        cvssv_3_to=cvssv_3_to,
        occurrences_from=occurrences_from,
        occurrences_to=occurrences_to,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    show_inactive: Union[Unset, bool] = UNSET,
    severity: Union[Unset, str] = UNSET,
    publish_date_from: Union[Unset, str] = UNSET,
    publish_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
    cvssv_2_from: Union[Unset, str] = UNSET,
    cvssv_2_to: Union[Unset, str] = UNSET,
    cvssv_3_from: Union[Unset, str] = UNSET,
    cvssv_3_to: Union[Unset, str] = UNSET,
    occurrences_from: Union[Unset, str] = UNSET,
    occurrences_to: Union[Unset, str] = UNSET,
) -> Response[Union[Any, list["Finding"]]]:
    """Returns a list of all findings grouped by vulnerability

     <p>Requires permission <strong>VIEW_VULNERABILITY</strong></p>

    Args:
        show_inactive (Union[Unset, bool]):
        severity (Union[Unset, str]):
        publish_date_from (Union[Unset, str]):
        publish_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):
        cvssv_2_from (Union[Unset, str]):
        cvssv_2_to (Union[Unset, str]):
        cvssv_3_from (Union[Unset, str]):
        cvssv_3_to (Union[Unset, str]):
        occurrences_from (Union[Unset, str]):
        occurrences_to (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['Finding']]]
    """

    kwargs = _get_kwargs(
        show_inactive=show_inactive,
        severity=severity,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        text_search_field=text_search_field,
        text_search_input=text_search_input,
        cvssv_2_from=cvssv_2_from,
        cvssv_2_to=cvssv_2_to,
        cvssv_3_from=cvssv_3_from,
        cvssv_3_to=cvssv_3_to,
        occurrences_from=occurrences_from,
        occurrences_to=occurrences_to,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    show_inactive: Union[Unset, bool] = UNSET,
    severity: Union[Unset, str] = UNSET,
    publish_date_from: Union[Unset, str] = UNSET,
    publish_date_to: Union[Unset, str] = UNSET,
    text_search_field: Union[Unset, str] = UNSET,
    text_search_input: Union[Unset, str] = UNSET,
    cvssv_2_from: Union[Unset, str] = UNSET,
    cvssv_2_to: Union[Unset, str] = UNSET,
    cvssv_3_from: Union[Unset, str] = UNSET,
    cvssv_3_to: Union[Unset, str] = UNSET,
    occurrences_from: Union[Unset, str] = UNSET,
    occurrences_to: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, list["Finding"]]]:
    """Returns a list of all findings grouped by vulnerability

     <p>Requires permission <strong>VIEW_VULNERABILITY</strong></p>

    Args:
        show_inactive (Union[Unset, bool]):
        severity (Union[Unset, str]):
        publish_date_from (Union[Unset, str]):
        publish_date_to (Union[Unset, str]):
        text_search_field (Union[Unset, str]):
        text_search_input (Union[Unset, str]):
        cvssv_2_from (Union[Unset, str]):
        cvssv_2_to (Union[Unset, str]):
        cvssv_3_from (Union[Unset, str]):
        cvssv_3_to (Union[Unset, str]):
        occurrences_from (Union[Unset, str]):
        occurrences_to (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['Finding']]
    """

    return (
        await asyncio_detailed(
            client=client,
            show_inactive=show_inactive,
            severity=severity,
            publish_date_from=publish_date_from,
            publish_date_to=publish_date_to,
            text_search_field=text_search_field,
            text_search_input=text_search_input,
            cvssv_2_from=cvssv_2_from,
            cvssv_2_to=cvssv_2_to,
            cvssv_3_from=cvssv_3_from,
            cvssv_3_to=cvssv_3_to,
            occurrences_from=occurrences_from,
            occurrences_to=occurrences_to,
        )
    ).parsed
