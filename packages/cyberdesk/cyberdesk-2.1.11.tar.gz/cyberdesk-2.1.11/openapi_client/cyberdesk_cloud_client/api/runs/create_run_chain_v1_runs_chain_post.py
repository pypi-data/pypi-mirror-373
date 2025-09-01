from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.workflow_chain_create import WorkflowChainCreate
from ...models.workflow_chain_response import WorkflowChainResponse
from ...types import Response


def _get_kwargs(
    *,
    body: WorkflowChainCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/runs/chain",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, WorkflowChainResponse]]:
    if response.status_code == 201:
        response_201 = WorkflowChainResponse.from_dict(response.json())

        return response_201
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, WorkflowChainResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: WorkflowChainCreate,
) -> Response[Union[HTTPValidationError, WorkflowChainResponse]]:
    """Create Run Chain

     Create a multi-step chain that runs on a single reserved session/machine.

    - Starts a new session unless session_id is provided (then runs on existing session).
    - Accepts shared_inputs/sensitive/file_inputs and per-step file_inputs.
    - machine_id > pool_id when starting a new session; both ignored if session_id provided.

    Args:
        body (WorkflowChainCreate): Request to create and run a multi-step chain on a single
            reserved session/machine

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, WorkflowChainResponse]]
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
    body: WorkflowChainCreate,
) -> Optional[Union[HTTPValidationError, WorkflowChainResponse]]:
    """Create Run Chain

     Create a multi-step chain that runs on a single reserved session/machine.

    - Starts a new session unless session_id is provided (then runs on existing session).
    - Accepts shared_inputs/sensitive/file_inputs and per-step file_inputs.
    - machine_id > pool_id when starting a new session; both ignored if session_id provided.

    Args:
        body (WorkflowChainCreate): Request to create and run a multi-step chain on a single
            reserved session/machine

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, WorkflowChainResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: WorkflowChainCreate,
) -> Response[Union[HTTPValidationError, WorkflowChainResponse]]:
    """Create Run Chain

     Create a multi-step chain that runs on a single reserved session/machine.

    - Starts a new session unless session_id is provided (then runs on existing session).
    - Accepts shared_inputs/sensitive/file_inputs and per-step file_inputs.
    - machine_id > pool_id when starting a new session; both ignored if session_id provided.

    Args:
        body (WorkflowChainCreate): Request to create and run a multi-step chain on a single
            reserved session/machine

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, WorkflowChainResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: WorkflowChainCreate,
) -> Optional[Union[HTTPValidationError, WorkflowChainResponse]]:
    """Create Run Chain

     Create a multi-step chain that runs on a single reserved session/machine.

    - Starts a new session unless session_id is provided (then runs on existing session).
    - Accepts shared_inputs/sensitive/file_inputs and per-step file_inputs.
    - machine_id > pool_id when starting a new session; both ignored if session_id provided.

    Args:
        body (WorkflowChainCreate): Request to create and run a multi-step chain on a single
            reserved session/machine

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, WorkflowChainResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
