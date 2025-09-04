from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.config_property import ConfigProperty
from ...types import Response


def _get_kwargs(
    group_name: str,
    property_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/configProperty/public/{group_name}/{property_name}".format(
            group_name=group_name,
            property_name=property_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ConfigProperty]]:
    if response.status_code == 200:
        response_200 = ConfigProperty.from_dict(response.json())

        return response_200

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ConfigProperty]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group_name: str,
    property_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, ConfigProperty]]:
    """Returns a public ConfigProperty

     <p></p>

    Args:
        group_name (str):
        property_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ConfigProperty]]
    """

    kwargs = _get_kwargs(
        group_name=group_name,
        property_name=property_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group_name: str,
    property_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, ConfigProperty]]:
    """Returns a public ConfigProperty

     <p></p>

    Args:
        group_name (str):
        property_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ConfigProperty]
    """

    return sync_detailed(
        group_name=group_name,
        property_name=property_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    group_name: str,
    property_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, ConfigProperty]]:
    """Returns a public ConfigProperty

     <p></p>

    Args:
        group_name (str):
        property_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ConfigProperty]]
    """

    kwargs = _get_kwargs(
        group_name=group_name,
        property_name=property_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group_name: str,
    property_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, ConfigProperty]]:
    """Returns a public ConfigProperty

     <p></p>

    Args:
        group_name (str):
        property_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ConfigProperty]
    """

    return (
        await asyncio_detailed(
            group_name=group_name,
            property_name=property_name,
            client=client,
        )
    ).parsed
