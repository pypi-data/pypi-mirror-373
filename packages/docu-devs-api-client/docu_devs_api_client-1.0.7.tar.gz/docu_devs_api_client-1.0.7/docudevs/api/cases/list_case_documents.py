from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.page_case_document import PageCaseDocument
from ...types import UNSET, Response


def _get_kwargs(
    case_id: int,
    *,
    page: int = 0,
    size: int = 20,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["size"] = size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/cases/{case_id}/documents",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PageCaseDocument]:
    if response.status_code == 200:
        response_200 = PageCaseDocument.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PageCaseDocument]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    page: int = 0,
    size: int = 20,
) -> Response[PageCaseDocument]:
    """
    Args:
        case_id (int):
        page (int):  Default: 0.
        size (int):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PageCaseDocument]
    """

    kwargs = _get_kwargs(
        case_id=case_id,
        page=page,
        size=size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    page: int = 0,
    size: int = 20,
) -> Optional[PageCaseDocument]:
    """
    Args:
        case_id (int):
        page (int):  Default: 0.
        size (int):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PageCaseDocument
    """

    return sync_detailed(
        case_id=case_id,
        client=client,
        page=page,
        size=size,
    ).parsed


async def asyncio_detailed(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    page: int = 0,
    size: int = 20,
) -> Response[PageCaseDocument]:
    """
    Args:
        case_id (int):
        page (int):  Default: 0.
        size (int):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PageCaseDocument]
    """

    kwargs = _get_kwargs(
        case_id=case_id,
        page=page,
        size=size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    page: int = 0,
    size: int = 20,
) -> Optional[PageCaseDocument]:
    """
    Args:
        case_id (int):
        page (int):  Default: 0.
        size (int):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PageCaseDocument
    """

    return (
        await asyncio_detailed(
            case_id=case_id,
            client=client,
            page=page,
            size=size,
        )
    ).parsed
