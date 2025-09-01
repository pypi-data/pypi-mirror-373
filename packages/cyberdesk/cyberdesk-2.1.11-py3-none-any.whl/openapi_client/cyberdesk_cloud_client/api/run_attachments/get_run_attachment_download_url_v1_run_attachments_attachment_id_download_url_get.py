from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.run_attachment_download_url_response import RunAttachmentDownloadUrlResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    attachment_id: UUID,
    *,
    expires_in: Union[Unset, int] = 300,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["expires_in"] = expires_in

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/run-attachments/{attachment_id}/download-url",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]:
    if response.status_code == 200:
        response_200 = RunAttachmentDownloadUrlResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    attachment_id: UUID,
    *,
    client: AuthenticatedClient,
    expires_in: Union[Unset, int] = 300,
) -> Response[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]:
    """Get Run Attachment Download Url

     Get a signed download URL for a run attachment file.

    Returns a signed URL that triggers automatic download when accessed.

    Args:
        attachment_id: The ID of the attachment to download
        expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)

    Args:
        attachment_id (UUID):
        expires_in (Union[Unset, int]): URL expiration time in seconds (10-3600) Default: 300.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]
    """

    kwargs = _get_kwargs(
        attachment_id=attachment_id,
        expires_in=expires_in,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    attachment_id: UUID,
    *,
    client: AuthenticatedClient,
    expires_in: Union[Unset, int] = 300,
) -> Optional[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]:
    """Get Run Attachment Download Url

     Get a signed download URL for a run attachment file.

    Returns a signed URL that triggers automatic download when accessed.

    Args:
        attachment_id: The ID of the attachment to download
        expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)

    Args:
        attachment_id (UUID):
        expires_in (Union[Unset, int]): URL expiration time in seconds (10-3600) Default: 300.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]
    """

    return sync_detailed(
        attachment_id=attachment_id,
        client=client,
        expires_in=expires_in,
    ).parsed


async def asyncio_detailed(
    attachment_id: UUID,
    *,
    client: AuthenticatedClient,
    expires_in: Union[Unset, int] = 300,
) -> Response[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]:
    """Get Run Attachment Download Url

     Get a signed download URL for a run attachment file.

    Returns a signed URL that triggers automatic download when accessed.

    Args:
        attachment_id: The ID of the attachment to download
        expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)

    Args:
        attachment_id (UUID):
        expires_in (Union[Unset, int]): URL expiration time in seconds (10-3600) Default: 300.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]
    """

    kwargs = _get_kwargs(
        attachment_id=attachment_id,
        expires_in=expires_in,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    attachment_id: UUID,
    *,
    client: AuthenticatedClient,
    expires_in: Union[Unset, int] = 300,
) -> Optional[Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]]:
    """Get Run Attachment Download Url

     Get a signed download URL for a run attachment file.

    Returns a signed URL that triggers automatic download when accessed.

    Args:
        attachment_id: The ID of the attachment to download
        expires_in: URL expiration time in seconds (10-3600). Default: 300 (5 minutes)

    Args:
        attachment_id (UUID):
        expires_in (Union[Unset, int]): URL expiration time in seconds (10-3600) Default: 300.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RunAttachmentDownloadUrlResponse]
    """

    return (
        await asyncio_detailed(
            attachment_id=attachment_id,
            client=client,
            expires_in=expires_in,
        )
    ).parsed
