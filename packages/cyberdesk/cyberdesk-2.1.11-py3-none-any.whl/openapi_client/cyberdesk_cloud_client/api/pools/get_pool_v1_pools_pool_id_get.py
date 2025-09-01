from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.pool_with_machines import PoolWithMachines
from ...types import UNSET, Response, Unset


def _get_kwargs(
    pool_id: UUID,
    *,
    include_machines: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_machines"] = include_machines

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/pools/{pool_id}",
        "params": params,
    }

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
    include_machines: Union[Unset, bool] = False,
) -> Response[Union[HTTPValidationError, PoolWithMachines]]:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (Union[Unset, bool]): Include full machine details Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PoolWithMachines]]
    """

    kwargs = _get_kwargs(
        pool_id=pool_id,
        include_machines=include_machines,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    include_machines: Union[Unset, bool] = False,
) -> Optional[Union[HTTPValidationError, PoolWithMachines]]:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (Union[Unset, bool]): Include full machine details Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PoolWithMachines]
    """

    return sync_detailed(
        pool_id=pool_id,
        client=client,
        include_machines=include_machines,
    ).parsed


async def asyncio_detailed(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    include_machines: Union[Unset, bool] = False,
) -> Response[Union[HTTPValidationError, PoolWithMachines]]:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (Union[Unset, bool]): Include full machine details Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PoolWithMachines]]
    """

    kwargs = _get_kwargs(
        pool_id=pool_id,
        include_machines=include_machines,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    include_machines: Union[Unset, bool] = False,
) -> Optional[Union[HTTPValidationError, PoolWithMachines]]:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (Union[Unset, bool]): Include full machine details Default: False.

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
            include_machines=include_machines,
        )
    ).parsed
