from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.repo_info import RepoInfo
from ...models.repo_update_request import RepoUpdateRequest
from ...types import Response


def _get_kwargs(
    repo_id: UUID,
    *,
    body: RepoUpdateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/repo/{repo_id}/update",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RepoInfo]]:
    if response.status_code == 200:
        response_200 = RepoInfo.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RepoInfo]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RepoUpdateRequest,
) -> Response[Union[HTTPValidationError, RepoInfo]]:
    """Update Repo Contents

     Update the contents of a repository.

    Args:
        repo_id (UUID):
        body (RepoUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RepoInfo]]
    """

    kwargs = _get_kwargs(
        repo_id=repo_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RepoUpdateRequest,
) -> Optional[Union[HTTPValidationError, RepoInfo]]:
    """Update Repo Contents

     Update the contents of a repository.

    Args:
        repo_id (UUID):
        body (RepoUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RepoInfo]
    """

    return sync_detailed(
        repo_id=repo_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RepoUpdateRequest,
) -> Response[Union[HTTPValidationError, RepoInfo]]:
    """Update Repo Contents

     Update the contents of a repository.

    Args:
        repo_id (UUID):
        body (RepoUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RepoInfo]]
    """

    kwargs = _get_kwargs(
        repo_id=repo_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: RepoUpdateRequest,
) -> Optional[Union[HTTPValidationError, RepoInfo]]:
    """Update Repo Contents

     Update the contents of a repository.

    Args:
        repo_id (UUID):
        body (RepoUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RepoInfo]
    """

    return (
        await asyncio_detailed(
            repo_id=repo_id,
            client=client,
            body=body,
        )
    ).parsed
