from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.workflow_response import WorkflowResponse
from ...models.workflow_update import WorkflowUpdate
from ...types import Response


def _get_kwargs(
    workflow_id: UUID,
    *,
    body: WorkflowUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/workflows/{workflow_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, WorkflowResponse]]:
    if response.status_code == 200:
        response_200 = WorkflowResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, WorkflowResponse]]:
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
    body: WorkflowUpdate,
) -> Response[Union[HTTPValidationError, WorkflowResponse]]:
    """Update Workflow

     Update a workflow's prompts.

    The current version will be saved to the version history.
    Only the fields provided in the request body will be updated.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):
        body (WorkflowUpdate): Schema for updating a workflow

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, WorkflowResponse]]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workflow_id: UUID,
    *,
    client: AuthenticatedClient,
    body: WorkflowUpdate,
) -> Optional[Union[HTTPValidationError, WorkflowResponse]]:
    """Update Workflow

     Update a workflow's prompts.

    The current version will be saved to the version history.
    Only the fields provided in the request body will be updated.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):
        body (WorkflowUpdate): Schema for updating a workflow

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, WorkflowResponse]
    """

    return sync_detailed(
        workflow_id=workflow_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    workflow_id: UUID,
    *,
    client: AuthenticatedClient,
    body: WorkflowUpdate,
) -> Response[Union[HTTPValidationError, WorkflowResponse]]:
    """Update Workflow

     Update a workflow's prompts.

    The current version will be saved to the version history.
    Only the fields provided in the request body will be updated.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):
        body (WorkflowUpdate): Schema for updating a workflow

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, WorkflowResponse]]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workflow_id: UUID,
    *,
    client: AuthenticatedClient,
    body: WorkflowUpdate,
) -> Optional[Union[HTTPValidationError, WorkflowResponse]]:
    """Update Workflow

     Update a workflow's prompts.

    The current version will be saved to the version history.
    Only the fields provided in the request body will be updated.
    The workflow must belong to the authenticated organization.

    Args:
        workflow_id (UUID):
        body (WorkflowUpdate): Schema for updating a workflow

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, WorkflowResponse]
    """

    return (
        await asyncio_detailed(
            workflow_id=workflow_id,
            client=client,
            body=body,
        )
    ).parsed
