from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.page_processing_job import PageProcessingJob
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[None, Unset, int] = UNSET,
    size: Union[None, Unset, int] = UNSET,
    sort: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    created_at_from: Union[None, Unset, str] = UNSET,
    created_at_to: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_page: Union[None, Unset, int]
    if isinstance(page, Unset):
        json_page = UNSET
    else:
        json_page = page
    params["page"] = json_page

    json_size: Union[None, Unset, int]
    if isinstance(size, Unset):
        json_size = UNSET
    else:
        json_size = size
    params["size"] = json_size

    json_sort: Union[None, Unset, str]
    if isinstance(sort, Unset):
        json_sort = UNSET
    else:
        json_sort = sort
    params["sort"] = json_sort

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_created_at_from: Union[None, Unset, str]
    if isinstance(created_at_from, Unset):
        json_created_at_from = UNSET
    else:
        json_created_at_from = created_at_from
    params["createdAtFrom"] = json_created_at_from

    json_created_at_to: Union[None, Unset, str]
    if isinstance(created_at_to, Unset):
        json_created_at_to = UNSET
    else:
        json_created_at_to = created_at_to
    params["createdAtTo"] = json_created_at_to

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/job/list",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PageProcessingJob]:
    if response.status_code == 200:
        response_200 = PageProcessingJob.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PageProcessingJob]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[None, Unset, int] = UNSET,
    size: Union[None, Unset, int] = UNSET,
    sort: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    created_at_from: Union[None, Unset, str] = UNSET,
    created_at_to: Union[None, Unset, str] = UNSET,
) -> Response[PageProcessingJob]:
    """
    Args:
        page (Union[None, Unset, int]):
        size (Union[None, Unset, int]):
        sort (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        created_at_from (Union[None, Unset, str]):
        created_at_to (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PageProcessingJob]
    """

    kwargs = _get_kwargs(
        page=page,
        size=size,
        sort=sort,
        status=status,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[None, Unset, int] = UNSET,
    size: Union[None, Unset, int] = UNSET,
    sort: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    created_at_from: Union[None, Unset, str] = UNSET,
    created_at_to: Union[None, Unset, str] = UNSET,
) -> Optional[PageProcessingJob]:
    """
    Args:
        page (Union[None, Unset, int]):
        size (Union[None, Unset, int]):
        sort (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        created_at_from (Union[None, Unset, str]):
        created_at_to (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PageProcessingJob
    """

    return sync_detailed(
        client=client,
        page=page,
        size=size,
        sort=sort,
        status=status,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[None, Unset, int] = UNSET,
    size: Union[None, Unset, int] = UNSET,
    sort: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    created_at_from: Union[None, Unset, str] = UNSET,
    created_at_to: Union[None, Unset, str] = UNSET,
) -> Response[PageProcessingJob]:
    """
    Args:
        page (Union[None, Unset, int]):
        size (Union[None, Unset, int]):
        sort (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        created_at_from (Union[None, Unset, str]):
        created_at_to (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PageProcessingJob]
    """

    kwargs = _get_kwargs(
        page=page,
        size=size,
        sort=sort,
        status=status,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[None, Unset, int] = UNSET,
    size: Union[None, Unset, int] = UNSET,
    sort: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    created_at_from: Union[None, Unset, str] = UNSET,
    created_at_to: Union[None, Unset, str] = UNSET,
) -> Optional[PageProcessingJob]:
    """
    Args:
        page (Union[None, Unset, int]):
        size (Union[None, Unset, int]):
        sort (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        created_at_from (Union[None, Unset, str]):
        created_at_to (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PageProcessingJob
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            size=size,
            sort=sort,
            status=status,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
        )
    ).parsed
