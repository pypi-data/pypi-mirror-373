from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.run_create import RunCreate
from ...models.run_response import RunResponse
from ...types import Response


def _get_kwargs(
    *,
    body: RunCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/runs",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RunResponse]]:
    if response.status_code == 201:
        response_201 = RunResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RunResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: RunCreate,
) -> Response[Union[HTTPValidationError, RunResponse]]:
    """Create Run

     Create a new run.

    The workflow must exist and belong to the authenticated organization.
    If machine_id is not provided, an available machine will be automatically selected.
    The run will be created with SCHEDULING status and a Temporal workflow will be started
    asynchronously.

    Args:
        body (RunCreate): Schema for creating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunResponse]]
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
    body: RunCreate,
) -> Optional[Union[HTTPValidationError, RunResponse]]:
    """Create Run

     Create a new run.

    The workflow must exist and belong to the authenticated organization.
    If machine_id is not provided, an available machine will be automatically selected.
    The run will be created with SCHEDULING status and a Temporal workflow will be started
    asynchronously.

    Args:
        body (RunCreate): Schema for creating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: RunCreate,
) -> Response[Union[HTTPValidationError, RunResponse]]:
    """Create Run

     Create a new run.

    The workflow must exist and belong to the authenticated organization.
    If machine_id is not provided, an available machine will be automatically selected.
    The run will be created with SCHEDULING status and a Temporal workflow will be started
    asynchronously.

    Args:
        body (RunCreate): Schema for creating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: RunCreate,
) -> Optional[Union[HTTPValidationError, RunResponse]]:
    """Create Run

     Create a new run.

    The workflow must exist and belong to the authenticated organization.
    If machine_id is not provided, an available machine will be automatically selected.
    The run will be created with SCHEDULING status and a Temporal workflow will be started
    asynchronously.

    Args:
        body (RunCreate): Schema for creating a run

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
