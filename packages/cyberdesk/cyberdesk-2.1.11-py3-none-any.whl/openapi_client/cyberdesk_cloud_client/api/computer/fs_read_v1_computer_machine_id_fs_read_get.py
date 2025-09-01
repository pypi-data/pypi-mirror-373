from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.fs_read_v1_computer_machine_id_fs_read_get_response_fs_read_v1_computer_machine_id_fs_read_get import (
    FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    machine_id: str,
    *,
    path: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["path"] = path

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/computer/{machine_id}/fs/read",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet.from_dict(
            response.json()
        )

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
) -> Response[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]:
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
    path: str,
) -> Response[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]:
    """Read file contents

     Read file contents from the machine (base64 encoded).

    Args:
        machine_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        machine_id=machine_id,
        path=path,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    path: str,
) -> Optional[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]:
    """Read file contents

     Read file contents from the machine (base64 encoded).

    Args:
        machine_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]
    """

    return sync_detailed(
        machine_id=machine_id,
        client=client,
        path=path,
    ).parsed


async def asyncio_detailed(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    path: str,
) -> Response[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]:
    """Read file contents

     Read file contents from the machine (base64 encoded).

    Args:
        machine_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        machine_id=machine_id,
        path=path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    path: str,
) -> Optional[Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]]:
    """Read file contents

     Read file contents from the machine (base64 encoded).

    Args:
        machine_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            machine_id=machine_id,
            client=client,
            path=path,
        )
    ).parsed
