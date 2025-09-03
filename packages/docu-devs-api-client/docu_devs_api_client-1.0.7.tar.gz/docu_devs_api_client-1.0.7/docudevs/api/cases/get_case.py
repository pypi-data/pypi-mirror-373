from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.case import Case
from ...types import Response


def _get_kwargs(
    case_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/cases/{case_id}",
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Case]:
    if response.status_code == 200:
        response_200 = Case.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Case]:
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
) -> Response[Case]:
    """
    Args:
        case_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Case]
    """

    kwargs = _get_kwargs(
        case_id=case_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Case]:
    """
    Args:
        case_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Case
    """

    return sync_detailed(
        case_id=case_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Case]:
    """
    Args:
        case_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Case]
    """

    kwargs = _get_kwargs(
        case_id=case_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Case]:
    """
    Args:
        case_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Case
    """

    return (
        await asyncio_detailed(
            case_id=case_id,
            client=client,
        )
    ).parsed
