from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connection_response import ConnectionResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    connection_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/connections/{connection_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ConnectionResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ConnectionResponse.from_dict(response.json())

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
) -> Response[Union[ConnectionResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connection_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ConnectionResponse, HTTPValidationError]]:
    """Get Connection

     Get a specific connection by ID.

    The connection must belong to a machine owned by the authenticated organization.

    Args:
        connection_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connection_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConnectionResponse, HTTPValidationError]]:
    """Get Connection

     Get a specific connection by ID.

    The connection must belong to a machine owned by the authenticated organization.

    Args:
        connection_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionResponse, HTTPValidationError]
    """

    return sync_detailed(
        connection_id=connection_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    connection_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ConnectionResponse, HTTPValidationError]]:
    """Get Connection

     Get a specific connection by ID.

    The connection must belong to a machine owned by the authenticated organization.

    Args:
        connection_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connection_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ConnectionResponse, HTTPValidationError]]:
    """Get Connection

     Get a specific connection by ID.

    The connection must belong to a machine owned by the authenticated organization.

    Args:
        connection_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            connection_id=connection_id,
            client=client,
        )
    ).parsed
