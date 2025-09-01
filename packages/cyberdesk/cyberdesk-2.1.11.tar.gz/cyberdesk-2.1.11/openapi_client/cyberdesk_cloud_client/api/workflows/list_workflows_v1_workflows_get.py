import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.paginated_response_workflow_response import PaginatedResponseWorkflowResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    created_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    created_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_created_at_from: Union[None, Unset, str]
    if isinstance(created_at_from, Unset):
        json_created_at_from = UNSET
    elif isinstance(created_at_from, datetime.datetime):
        json_created_at_from = created_at_from.isoformat()
    else:
        json_created_at_from = created_at_from
    params["created_at_from"] = json_created_at_from

    json_created_at_to: Union[None, Unset, str]
    if isinstance(created_at_to, Unset):
        json_created_at_to = UNSET
    elif isinstance(created_at_to, datetime.datetime):
        json_created_at_to = created_at_to.isoformat()
    else:
        json_created_at_to = created_at_to
    params["created_at_to"] = json_created_at_to

    json_updated_at_from: Union[None, Unset, str]
    if isinstance(updated_at_from, Unset):
        json_updated_at_from = UNSET
    elif isinstance(updated_at_from, datetime.datetime):
        json_updated_at_from = updated_at_from.isoformat()
    else:
        json_updated_at_from = updated_at_from
    params["updated_at_from"] = json_updated_at_from

    json_updated_at_to: Union[None, Unset, str]
    if isinstance(updated_at_to, Unset):
        json_updated_at_to = UNSET
    elif isinstance(updated_at_to, datetime.datetime):
        json_updated_at_to = updated_at_to.isoformat()
    else:
        json_updated_at_to = updated_at_to
    params["updated_at_to"] = json_updated_at_to

    params["skip"] = skip

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/workflows",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]:
    if response.status_code == 200:
        response_200 = PaginatedResponseWorkflowResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    created_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    created_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
) -> Response[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]:
    """List Workflows

     List all workflows for the authenticated organization.

    Supports pagination and returns workflows ordered by updated_at descending.

    Args:
        created_at_from (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            after this ISO timestamp (UTC)
        created_at_to (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            before this ISO timestamp (UTC)
        updated_at_from (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            after this ISO timestamp (UTC)
        updated_at_to (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            before this ISO timestamp (UTC)
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]
    """

    kwargs = _get_kwargs(
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
        skip=skip,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    created_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    created_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
) -> Optional[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]:
    """List Workflows

     List all workflows for the authenticated organization.

    Supports pagination and returns workflows ordered by updated_at descending.

    Args:
        created_at_from (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            after this ISO timestamp (UTC)
        created_at_to (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            before this ISO timestamp (UTC)
        updated_at_from (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            after this ISO timestamp (UTC)
        updated_at_to (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            before this ISO timestamp (UTC)
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PaginatedResponseWorkflowResponse]
    """

    return sync_detailed(
        client=client,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
        skip=skip,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    created_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    created_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
) -> Response[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]:
    """List Workflows

     List all workflows for the authenticated organization.

    Supports pagination and returns workflows ordered by updated_at descending.

    Args:
        created_at_from (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            after this ISO timestamp (UTC)
        created_at_to (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            before this ISO timestamp (UTC)
        updated_at_from (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            after this ISO timestamp (UTC)
        updated_at_to (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            before this ISO timestamp (UTC)
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]
    """

    kwargs = _get_kwargs(
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
        skip=skip,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    created_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    created_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_from: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_to: Union[None, Unset, datetime.datetime] = UNSET,
    skip: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
) -> Optional[Union[HTTPValidationError, PaginatedResponseWorkflowResponse]]:
    """List Workflows

     List all workflows for the authenticated organization.

    Supports pagination and returns workflows ordered by updated_at descending.

    Args:
        created_at_from (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            after this ISO timestamp (UTC)
        created_at_to (Union[None, Unset, datetime.datetime]): Filter workflows created at or
            before this ISO timestamp (UTC)
        updated_at_from (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            after this ISO timestamp (UTC)
        updated_at_to (Union[None, Unset, datetime.datetime]): Filter workflows updated at or
            before this ISO timestamp (UTC)
        skip (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PaginatedResponseWorkflowResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            updated_at_from=updated_at_from,
            updated_at_to=updated_at_to,
            skip=skip,
            limit=limit,
        )
    ).parsed
