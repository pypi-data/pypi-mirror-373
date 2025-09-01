from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.trajectory_response import TrajectoryResponse
from ...types import Response


def _get_kwargs(
    workflow_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/workflows/{workflow_id}/latest-trajectory",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, TrajectoryResponse]]:
    if response.status_code == 200:
        response_200 = TrajectoryResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, TrajectoryResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workflow_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, TrajectoryResponse]]:
    """Get Latest Trajectory For Workflow

     Get the latest trajectory for a specific workflow.

    Returns the most recently updated trajectory for the workflow.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TrajectoryResponse]]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workflow_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, TrajectoryResponse]]:
    """Get Latest Trajectory For Workflow

     Get the latest trajectory for a specific workflow.

    Returns the most recently updated trajectory for the workflow.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TrajectoryResponse]
    """

    return sync_detailed(
        workflow_id=workflow_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    workflow_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, TrajectoryResponse]]:
    """Get Latest Trajectory For Workflow

     Get the latest trajectory for a specific workflow.

    Returns the most recently updated trajectory for the workflow.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, TrajectoryResponse]]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workflow_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, TrajectoryResponse]]:
    """Get Latest Trajectory For Workflow

     Get the latest trajectory for a specific workflow.

    Returns the most recently updated trajectory for the workflow.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, TrajectoryResponse]
    """

    return (
        await asyncio_detailed(
            workflow_id=workflow_id,
            client=client,
        )
    ).parsed
