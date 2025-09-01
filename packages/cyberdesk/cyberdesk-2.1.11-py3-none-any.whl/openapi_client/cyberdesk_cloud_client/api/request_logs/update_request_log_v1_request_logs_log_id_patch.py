from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.request_log_response import RequestLogResponse
from ...models.request_log_update import RequestLogUpdate
from ...types import Response


def _get_kwargs(
    log_id: UUID,
    *,
    body: RequestLogUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/request-logs/{log_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RequestLogResponse]]:
    if response.status_code == 200:
        response_200 = RequestLogResponse.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, RequestLogResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    log_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RequestLogUpdate,
) -> Response[Union[HTTPValidationError, RequestLogResponse]]:
    """Update Request Log

     Update a request log with response data.

    This is typically called when a request completes to add the response details.
    Only the fields provided in the request body will be updated.
    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):
        body (RequestLogUpdate): Schema for updating a request log

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RequestLogResponse]]
    """

    kwargs = _get_kwargs(
        log_id=log_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    log_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RequestLogUpdate,
) -> Optional[Union[HTTPValidationError, RequestLogResponse]]:
    """Update Request Log

     Update a request log with response data.

    This is typically called when a request completes to add the response details.
    Only the fields provided in the request body will be updated.
    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):
        body (RequestLogUpdate): Schema for updating a request log

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RequestLogResponse]
    """

    return sync_detailed(
        log_id=log_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    log_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RequestLogUpdate,
) -> Response[Union[HTTPValidationError, RequestLogResponse]]:
    """Update Request Log

     Update a request log with response data.

    This is typically called when a request completes to add the response details.
    Only the fields provided in the request body will be updated.
    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):
        body (RequestLogUpdate): Schema for updating a request log

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RequestLogResponse]]
    """

    kwargs = _get_kwargs(
        log_id=log_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    log_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RequestLogUpdate,
) -> Optional[Union[HTTPValidationError, RequestLogResponse]]:
    """Update Request Log

     Update a request log with response data.

    This is typically called when a request completes to add the response details.
    Only the fields provided in the request body will be updated.
    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):
        body (RequestLogUpdate): Schema for updating a request log

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RequestLogResponse]
    """

    return (
        await asyncio_detailed(
            log_id=log_id,
            client=client,
            body=body,
        )
    ).parsed
