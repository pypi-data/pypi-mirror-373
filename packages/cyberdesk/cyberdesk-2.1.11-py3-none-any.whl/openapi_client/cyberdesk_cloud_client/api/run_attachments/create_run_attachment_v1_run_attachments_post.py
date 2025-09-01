from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.run_attachment_create import RunAttachmentCreate
from ...models.run_attachment_response import RunAttachmentResponse
from ...types import Response


def _get_kwargs(
    *,
    body: RunAttachmentCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/run-attachments",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RunAttachmentResponse]]:
    if response.status_code == 201:
        response_201 = RunAttachmentResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RunAttachmentResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: RunAttachmentCreate,
) -> Response[Union[HTTPValidationError, RunAttachmentResponse]]:
    """Create Run Attachment

     Create a new run attachment.

    This endpoint is primarily for internal use. File uploads typically happen
    through the run creation endpoint.

    Args:
        body (RunAttachmentCreate): Schema for creating a run attachment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunAttachmentResponse]]
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
    body: RunAttachmentCreate,
) -> Optional[Union[HTTPValidationError, RunAttachmentResponse]]:
    """Create Run Attachment

     Create a new run attachment.

    This endpoint is primarily for internal use. File uploads typically happen
    through the run creation endpoint.

    Args:
        body (RunAttachmentCreate): Schema for creating a run attachment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunAttachmentResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: RunAttachmentCreate,
) -> Response[Union[HTTPValidationError, RunAttachmentResponse]]:
    """Create Run Attachment

     Create a new run attachment.

    This endpoint is primarily for internal use. File uploads typically happen
    through the run creation endpoint.

    Args:
        body (RunAttachmentCreate): Schema for creating a run attachment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunAttachmentResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: RunAttachmentCreate,
) -> Optional[Union[HTTPValidationError, RunAttachmentResponse]]:
    """Create Run Attachment

     Create a new run attachment.

    This endpoint is primarily for internal use. File uploads typically happen
    through the run creation endpoint.

    Args:
        body (RunAttachmentCreate): Schema for creating a run attachment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunAttachmentResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
