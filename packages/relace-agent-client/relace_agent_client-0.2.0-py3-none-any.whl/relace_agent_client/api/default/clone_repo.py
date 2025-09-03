from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.repo_clone_response import RepoCloneResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    repo_id: UUID,
    *,
    commit: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_commit: Union[None, Unset, str]
    if isinstance(commit, Unset):
        json_commit = UNSET
    else:
        json_commit = commit
    params["commit"] = json_commit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/repo/{repo_id}/clone",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RepoCloneResponse]]:
    if response.status_code == 200:
        response_200 = RepoCloneResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RepoCloneResponse]]:
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
    commit: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, RepoCloneResponse]]:
    """Clone Repo

     Return all readable tracked files in a repository.

    If a `commit` is provided, read file contents from that commit; otherwise
    read from the working directory.

    Args:
        repo_id (UUID):
        commit (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RepoCloneResponse]]
    """

    kwargs = _get_kwargs(
        repo_id=repo_id,
        commit=commit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    commit: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, RepoCloneResponse]]:
    """Clone Repo

     Return all readable tracked files in a repository.

    If a `commit` is provided, read file contents from that commit; otherwise
    read from the working directory.

    Args:
        repo_id (UUID):
        commit (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RepoCloneResponse]
    """

    return sync_detailed(
        repo_id=repo_id,
        client=client,
        commit=commit,
    ).parsed


async def asyncio_detailed(
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    commit: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, RepoCloneResponse]]:
    """Clone Repo

     Return all readable tracked files in a repository.

    If a `commit` is provided, read file contents from that commit; otherwise
    read from the working directory.

    Args:
        repo_id (UUID):
        commit (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RepoCloneResponse]]
    """

    kwargs = _get_kwargs(
        repo_id=repo_id,
        commit=commit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    commit: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, RepoCloneResponse]]:
    """Clone Repo

     Return all readable tracked files in a repository.

    If a `commit` is provided, read file contents from that commit; otherwise
    read from the working directory.

    Args:
        repo_id (UUID):
        commit (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RepoCloneResponse]
    """

    return (
        await asyncio_detailed(
            repo_id=repo_id,
            client=client,
            commit=commit,
        )
    ).parsed
