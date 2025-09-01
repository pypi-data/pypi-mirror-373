from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.request_log_response import RequestLogResponse
from ...types import Response


def _get_kwargs(
    log_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/request-logs/{log_id}",
    }

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
) -> Response[Union[HTTPValidationError, RequestLogResponse]]:
    """Get Request Log

     Get a specific request log by ID.

    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RequestLogResponse]]
    """

    kwargs = _get_kwargs(
        log_id=log_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    log_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, RequestLogResponse]]:
    """Get Request Log

     Get a specific request log by ID.

    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RequestLogResponse]
    """

    return sync_detailed(
        log_id=log_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    log_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, RequestLogResponse]]:
    """Get Request Log

     Get a specific request log by ID.

    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RequestLogResponse]]
    """

    kwargs = _get_kwargs(
        log_id=log_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    log_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, RequestLogResponse]]:
    """Get Request Log

     Get a specific request log by ID.

    The log must belong to a machine owned by the authenticated organization.

    Args:
        log_id (UUID):

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
        )
    ).parsed
