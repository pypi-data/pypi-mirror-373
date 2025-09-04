from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bom_upload_response import BomUploadResponse
from ...models.invalid_bom_problem_details import InvalidBomProblemDetails
from ...models.vex_submit_request import VexSubmitRequest
from ...types import Response


def _get_kwargs(
    *,
    body: VexSubmitRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/vex",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]:
    if response.status_code == 200:
        response_200 = BomUploadResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = InvalidBomProblemDetails.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: VexSubmitRequest,
) -> Response[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]:
    """Upload a supported VEX document

     <p>
      Expects CycloneDX and a valid project UUID. If a UUID is not specified,
      then the <code>projectName</code> and <code>projectVersion</code> must be specified.
    </p>
    <p>
      The VEX will be validated against the CycloneDX schema. If schema validation fails,
      a response with problem details in RFC 9457 format will be returned. In this case,
      the response's content type will be <code>application/problem+json</code>.
    </p>
    <p>
      The maximum allowed length of the <code>vex</code> value is 20'000'000 characters.
      When uploading large VEX files, the <code>POST</code> endpoint is preferred,
      as it does not have this limit.
    </p>
    <p>Requires permission <strong>VULNERABILITY_ANALYSIS</strong></p>

    Args:
        body (VexSubmitRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]
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
    body: VexSubmitRequest,
) -> Optional[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]:
    """Upload a supported VEX document

     <p>
      Expects CycloneDX and a valid project UUID. If a UUID is not specified,
      then the <code>projectName</code> and <code>projectVersion</code> must be specified.
    </p>
    <p>
      The VEX will be validated against the CycloneDX schema. If schema validation fails,
      a response with problem details in RFC 9457 format will be returned. In this case,
      the response's content type will be <code>application/problem+json</code>.
    </p>
    <p>
      The maximum allowed length of the <code>vex</code> value is 20'000'000 characters.
      When uploading large VEX files, the <code>POST</code> endpoint is preferred,
      as it does not have this limit.
    </p>
    <p>Requires permission <strong>VULNERABILITY_ANALYSIS</strong></p>

    Args:
        body (VexSubmitRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BomUploadResponse, InvalidBomProblemDetails]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: VexSubmitRequest,
) -> Response[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]:
    """Upload a supported VEX document

     <p>
      Expects CycloneDX and a valid project UUID. If a UUID is not specified,
      then the <code>projectName</code> and <code>projectVersion</code> must be specified.
    </p>
    <p>
      The VEX will be validated against the CycloneDX schema. If schema validation fails,
      a response with problem details in RFC 9457 format will be returned. In this case,
      the response's content type will be <code>application/problem+json</code>.
    </p>
    <p>
      The maximum allowed length of the <code>vex</code> value is 20'000'000 characters.
      When uploading large VEX files, the <code>POST</code> endpoint is preferred,
      as it does not have this limit.
    </p>
    <p>Requires permission <strong>VULNERABILITY_ANALYSIS</strong></p>

    Args:
        body (VexSubmitRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: VexSubmitRequest,
) -> Optional[Union[Any, BomUploadResponse, InvalidBomProblemDetails]]:
    """Upload a supported VEX document

     <p>
      Expects CycloneDX and a valid project UUID. If a UUID is not specified,
      then the <code>projectName</code> and <code>projectVersion</code> must be specified.
    </p>
    <p>
      The VEX will be validated against the CycloneDX schema. If schema validation fails,
      a response with problem details in RFC 9457 format will be returned. In this case,
      the response's content type will be <code>application/problem+json</code>.
    </p>
    <p>
      The maximum allowed length of the <code>vex</code> value is 20'000'000 characters.
      When uploading large VEX files, the <code>POST</code> endpoint is preferred,
      as it does not have this limit.
    </p>
    <p>Requires permission <strong>VULNERABILITY_ANALYSIS</strong></p>

    Args:
        body (VexSubmitRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BomUploadResponse, InvalidBomProblemDetails]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
