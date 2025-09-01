from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.keyboard_key_request import KeyboardKeyRequest
from ...types import Response


def _get_kwargs(
    machine_id: str,
    *,
    body: KeyboardKeyRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/computer/{machine_id}/input/keyboard/key",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: KeyboardKeyRequest,
) -> Response[Union[Any, HTTPValidationError]]:
    """Send key combination

     Send a key combination (e.g., 'ctrl+a', 'alt+tab'). Uses 'keys' field to match Piglet expectations.

    Args:
        machine_id (str):
        body (KeyboardKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        machine_id=machine_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: KeyboardKeyRequest,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Send key combination

     Send a key combination (e.g., 'ctrl+a', 'alt+tab'). Uses 'keys' field to match Piglet expectations.

    Args:
        machine_id (str):
        body (KeyboardKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        machine_id=machine_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: KeyboardKeyRequest,
) -> Response[Union[Any, HTTPValidationError]]:
    """Send key combination

     Send a key combination (e.g., 'ctrl+a', 'alt+tab'). Uses 'keys' field to match Piglet expectations.

    Args:
        machine_id (str):
        body (KeyboardKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        machine_id=machine_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: KeyboardKeyRequest,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Send key combination

     Send a key combination (e.g., 'ctrl+a', 'alt+tab'). Uses 'keys' field to match Piglet expectations.

    Args:
        machine_id (str):
        body (KeyboardKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            machine_id=machine_id,
            client=client,
            body=body,
        )
    ).parsed
