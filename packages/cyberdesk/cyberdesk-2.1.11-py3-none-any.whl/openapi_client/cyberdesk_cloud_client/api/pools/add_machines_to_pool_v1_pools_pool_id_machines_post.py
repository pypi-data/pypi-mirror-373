from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.machine_pool_assignment import MachinePoolAssignment
from ...models.pool_with_machines import PoolWithMachines
from ...types import Response


def _get_kwargs(
    pool_id: UUID,
    *,
    body: MachinePoolAssignment,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/pools/{pool_id}/machines",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PoolWithMachines]]:
    if response.status_code == 200:
        response_200 = PoolWithMachines.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PoolWithMachines]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MachinePoolAssignment,
) -> Response[Union[HTTPValidationError, PoolWithMachines]]:
    """Add Machines To Pool

     Add machines to a pool.

    Args:
        pool_id (UUID):
        body (MachinePoolAssignment): Schema for assigning machines to pools

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PoolWithMachines]]
    """

    kwargs = _get_kwargs(
        pool_id=pool_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MachinePoolAssignment,
) -> Optional[Union[HTTPValidationError, PoolWithMachines]]:
    """Add Machines To Pool

     Add machines to a pool.

    Args:
        pool_id (UUID):
        body (MachinePoolAssignment): Schema for assigning machines to pools

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PoolWithMachines]
    """

    return sync_detailed(
        pool_id=pool_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MachinePoolAssignment,
) -> Response[Union[HTTPValidationError, PoolWithMachines]]:
    """Add Machines To Pool

     Add machines to a pool.

    Args:
        pool_id (UUID):
        body (MachinePoolAssignment): Schema for assigning machines to pools

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PoolWithMachines]]
    """

    kwargs = _get_kwargs(
        pool_id=pool_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MachinePoolAssignment,
) -> Optional[Union[HTTPValidationError, PoolWithMachines]]:
    """Add Machines To Pool

     Add machines to a pool.

    Args:
        pool_id (UUID):
        body (MachinePoolAssignment): Schema for assigning machines to pools

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PoolWithMachines]
    """

    return (
        await asyncio_detailed(
            pool_id=pool_id,
            client=client,
            body=body,
        )
    ).parsed
