from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.run_response import RunResponse
from ...models.run_update import RunUpdate
from ...types import Response


def _get_kwargs(
    run_id: UUID,
    *,
    body: RunUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/runs/{run_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RunResponse]]:
    if response.status_code == 200:
        response_200 = RunResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RunResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    run_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RunUpdate,
) -> Response[Union[HTTPValidationError, RunResponse]]:
    """Update Run

     Update a run's data.

    Only the fields provided in the request body will be updated.
    The run must belong to the authenticated organization.

    Args:
        run_id (UUID):
        body (RunUpdate): Schema for updating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunResponse]]
    """

    kwargs = _get_kwargs(
        run_id=run_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    run_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RunUpdate,
) -> Optional[Union[HTTPValidationError, RunResponse]]:
    """Update Run

     Update a run's data.

    Only the fields provided in the request body will be updated.
    The run must belong to the authenticated organization.

    Args:
        run_id (UUID):
        body (RunUpdate): Schema for updating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunResponse]
    """

    return sync_detailed(
        run_id=run_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    run_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RunUpdate,
) -> Response[Union[HTTPValidationError, RunResponse]]:
    """Update Run

     Update a run's data.

    Only the fields provided in the request body will be updated.
    The run must belong to the authenticated organization.

    Args:
        run_id (UUID):
        body (RunUpdate): Schema for updating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunResponse]]
    """

    kwargs = _get_kwargs(
        run_id=run_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    run_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RunUpdate,
) -> Optional[Union[HTTPValidationError, RunResponse]]:
    """Update Run

     Update a run's data.

    Only the fields provided in the request body will be updated.
    The run must belong to the authenticated organization.

    Args:
        run_id (UUID):
        body (RunUpdate): Schema for updating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunResponse]
    """

    return (
        await asyncio_detailed(
            run_id=run_id,
            client=client,
            body=body,
        )
    ).parsed
