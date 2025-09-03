from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ocr_command import OcrCommand
from ...models.upload_response import UploadResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    guid: str,
    *,
    body: OcrCommand,
    format_: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_format_: Union[None, Unset, str]
    if isinstance(format_, Unset):
        json_format_ = UNSET
    else:
        json_format_ = format_
    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/document/ocr/{guid}",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[UploadResponse]:
    if response.status_code == 200:
        response_200 = UploadResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[UploadResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrCommand,
    format_: Union[None, Unset, str] = UNSET,
) -> Response[UploadResponse]:
    """
    Args:
        guid (str):
        format_ (Union[None, Unset, str]):
        body (OcrCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        guid=guid,
        body=body,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrCommand,
    format_: Union[None, Unset, str] = UNSET,
) -> Optional[UploadResponse]:
    """
    Args:
        guid (str):
        format_ (Union[None, Unset, str]):
        body (OcrCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return sync_detailed(
        guid=guid,
        client=client,
        body=body,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrCommand,
    format_: Union[None, Unset, str] = UNSET,
) -> Response[UploadResponse]:
    """
    Args:
        guid (str):
        format_ (Union[None, Unset, str]):
        body (OcrCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        guid=guid,
        body=body,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrCommand,
    format_: Union[None, Unset, str] = UNSET,
) -> Optional[UploadResponse]:
    """
    Args:
        guid (str):
        format_ (Union[None, Unset, str]):
        body (OcrCommand):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return (
        await asyncio_detailed(
            guid=guid,
            client=client,
            body=body,
            format_=format_,
        )
    ).parsed
