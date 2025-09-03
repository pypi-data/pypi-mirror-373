import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_repo_metadata_order_by import ListRepoMetadataOrderBy
from ...models.paged_response_repo_metadata import PagedResponseRepoMetadata
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    filter_metadata: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, datetime.datetime] = UNSET,
    created_before: Union[None, Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, ListRepoMetadataOrderBy] = ListRepoMetadataOrderBy.CREATED_AT,
    order_descending: Union[Unset, bool] = False,
    page_start: Union[Unset, int] = 0,
    page_size: Union[Unset, int] = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_filter_metadata: Union[None, Unset, str]
    if isinstance(filter_metadata, Unset):
        json_filter_metadata = UNSET
    else:
        json_filter_metadata = filter_metadata
    params["filter_metadata"] = json_filter_metadata

    json_created_after: Union[None, Unset, str]
    if isinstance(created_after, Unset):
        json_created_after = UNSET
    elif isinstance(created_after, datetime.datetime):
        json_created_after = created_after.isoformat()
    else:
        json_created_after = created_after
    params["created_after"] = json_created_after

    json_created_before: Union[None, Unset, str]
    if isinstance(created_before, Unset):
        json_created_before = UNSET
    elif isinstance(created_before, datetime.datetime):
        json_created_before = created_before.isoformat()
    else:
        json_created_before = created_before
    params["created_before"] = json_created_before

    json_order_by: Union[Unset, str] = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["order_by"] = json_order_by

    params["order_descending"] = order_descending

    params["page_start"] = page_start

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/repo",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PagedResponseRepoMetadata]]:
    if response.status_code == 200:
        response_200 = PagedResponseRepoMetadata.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, PagedResponseRepoMetadata]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    filter_metadata: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, datetime.datetime] = UNSET,
    created_before: Union[None, Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, ListRepoMetadataOrderBy] = ListRepoMetadataOrderBy.CREATED_AT,
    order_descending: Union[Unset, bool] = False,
    page_start: Union[Unset, int] = 0,
    page_size: Union[Unset, int] = 100,
) -> Response[Union[HTTPValidationError, PagedResponseRepoMetadata]]:
    """List Repo Metadata

     Get metadata for all repositories owned by the user.

    Args:
        filter_metadata (Union[None, Unset, str]):
        created_after (Union[None, Unset, datetime.datetime]):
        created_before (Union[None, Unset, datetime.datetime]):
        order_by (Union[Unset, ListRepoMetadataOrderBy]):  Default:
            ListRepoMetadataOrderBy.CREATED_AT.
        order_descending (Union[Unset, bool]):  Default: False.
        page_start (Union[Unset, int]):  Default: 0.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PagedResponseRepoMetadata]]
    """

    kwargs = _get_kwargs(
        filter_metadata=filter_metadata,
        created_after=created_after,
        created_before=created_before,
        order_by=order_by,
        order_descending=order_descending,
        page_start=page_start,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    filter_metadata: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, datetime.datetime] = UNSET,
    created_before: Union[None, Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, ListRepoMetadataOrderBy] = ListRepoMetadataOrderBy.CREATED_AT,
    order_descending: Union[Unset, bool] = False,
    page_start: Union[Unset, int] = 0,
    page_size: Union[Unset, int] = 100,
) -> Optional[Union[HTTPValidationError, PagedResponseRepoMetadata]]:
    """List Repo Metadata

     Get metadata for all repositories owned by the user.

    Args:
        filter_metadata (Union[None, Unset, str]):
        created_after (Union[None, Unset, datetime.datetime]):
        created_before (Union[None, Unset, datetime.datetime]):
        order_by (Union[Unset, ListRepoMetadataOrderBy]):  Default:
            ListRepoMetadataOrderBy.CREATED_AT.
        order_descending (Union[Unset, bool]):  Default: False.
        page_start (Union[Unset, int]):  Default: 0.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PagedResponseRepoMetadata]
    """

    return sync_detailed(
        client=client,
        filter_metadata=filter_metadata,
        created_after=created_after,
        created_before=created_before,
        order_by=order_by,
        order_descending=order_descending,
        page_start=page_start,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    filter_metadata: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, datetime.datetime] = UNSET,
    created_before: Union[None, Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, ListRepoMetadataOrderBy] = ListRepoMetadataOrderBy.CREATED_AT,
    order_descending: Union[Unset, bool] = False,
    page_start: Union[Unset, int] = 0,
    page_size: Union[Unset, int] = 100,
) -> Response[Union[HTTPValidationError, PagedResponseRepoMetadata]]:
    """List Repo Metadata

     Get metadata for all repositories owned by the user.

    Args:
        filter_metadata (Union[None, Unset, str]):
        created_after (Union[None, Unset, datetime.datetime]):
        created_before (Union[None, Unset, datetime.datetime]):
        order_by (Union[Unset, ListRepoMetadataOrderBy]):  Default:
            ListRepoMetadataOrderBy.CREATED_AT.
        order_descending (Union[Unset, bool]):  Default: False.
        page_start (Union[Unset, int]):  Default: 0.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PagedResponseRepoMetadata]]
    """

    kwargs = _get_kwargs(
        filter_metadata=filter_metadata,
        created_after=created_after,
        created_before=created_before,
        order_by=order_by,
        order_descending=order_descending,
        page_start=page_start,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    filter_metadata: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, datetime.datetime] = UNSET,
    created_before: Union[None, Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, ListRepoMetadataOrderBy] = ListRepoMetadataOrderBy.CREATED_AT,
    order_descending: Union[Unset, bool] = False,
    page_start: Union[Unset, int] = 0,
    page_size: Union[Unset, int] = 100,
) -> Optional[Union[HTTPValidationError, PagedResponseRepoMetadata]]:
    """List Repo Metadata

     Get metadata for all repositories owned by the user.

    Args:
        filter_metadata (Union[None, Unset, str]):
        created_after (Union[None, Unset, datetime.datetime]):
        created_before (Union[None, Unset, datetime.datetime]):
        order_by (Union[Unset, ListRepoMetadataOrderBy]):  Default:
            ListRepoMetadataOrderBy.CREATED_AT.
        order_descending (Union[Unset, bool]):  Default: False.
        page_start (Union[Unset, int]):  Default: 0.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PagedResponseRepoMetadata]
    """

    return (
        await asyncio_detailed(
            client=client,
            filter_metadata=filter_metadata,
            created_after=created_after,
            created_before=created_before,
            order_by=order_by,
            order_descending=order_descending,
            page_start=page_start,
            page_size=page_size,
        )
    ).parsed
