from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.repo_retrieve_request import RepoRetrieveRequest
from ...models.repo_retrieve_response import RepoRetrieveResponse
from ...types import Response


def _get_kwargs(
    repo_id: UUID,
    *,
    body: RepoRetrieveRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/repo/{repo_id}/retrieve",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, RepoRetrieveResponse]]:
    if response.status_code == 200:
        response_200 = RepoRetrieveResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, RepoRetrieveResponse]]:
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
    body: RepoRetrieveRequest,
) -> Response[Union[HTTPValidationError, RepoRetrieveResponse]]:
    """Retrieve Relevant Content

     Retrieve relevant content from a repository based on a query.

    Args:
        repo_id (UUID):
        body (RepoRetrieveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RepoRetrieveResponse]]
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
    body: RepoRetrieveRequest,
) -> Optional[Union[HTTPValidationError, RepoRetrieveResponse]]:
    """Retrieve Relevant Content

     Retrieve relevant content from a repository based on a query.

    Args:
        repo_id (UUID):
        body (RepoRetrieveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RepoRetrieveResponse]
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
    body: RepoRetrieveRequest,
) -> Response[Union[HTTPValidationError, RepoRetrieveResponse]]:
    """Retrieve Relevant Content

     Retrieve relevant content from a repository based on a query.

    Args:
        repo_id (UUID):
        body (RepoRetrieveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, RepoRetrieveResponse]]
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
    body: RepoRetrieveRequest,
) -> Optional[Union[HTTPValidationError, RepoRetrieveResponse]]:
    """Retrieve Relevant Content

     Retrieve relevant content from a repository based on a query.

    Args:
        repo_id (UUID):
        body (RepoRetrieveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, RepoRetrieveResponse]
    """

    return (
        await asyncio_detailed(
            repo_id=repo_id,
            client=client,
            body=body,
        )
    ).parsed
