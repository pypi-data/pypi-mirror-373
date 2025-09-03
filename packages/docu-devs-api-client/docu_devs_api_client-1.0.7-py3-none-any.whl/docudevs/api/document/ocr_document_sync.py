from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ocr_document_sync_body import OcrDocumentSyncBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: OcrDocumentSyncBody,
    format_: Union[None, Unset, str] = UNSET,
    ocr: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_format_: Union[None, Unset, str]
    if isinstance(format_, Unset):
        json_format_ = UNSET
    else:
        json_format_ = format_
    params["format"] = json_format_

    json_ocr: Union[None, Unset, str]
    if isinstance(ocr, Unset):
        json_ocr = UNSET
    else:
        json_ocr = ocr
    params["ocr"] = json_ocr

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/document/ocr/sync",
        "params": params,
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[str]:
    if response.status_code == 200:
        response_200 = cast(str, response.json())
        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrDocumentSyncBody,
    format_: Union[None, Unset, str] = UNSET,
    ocr: Union[None, Unset, str] = UNSET,
) -> Response[str]:
    """
    Args:
        format_ (Union[None, Unset, str]):
        ocr (Union[None, Unset, str]):
        body (OcrDocumentSyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        body=body,
        format_=format_,
        ocr=ocr,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrDocumentSyncBody,
    format_: Union[None, Unset, str] = UNSET,
    ocr: Union[None, Unset, str] = UNSET,
) -> Optional[str]:
    """
    Args:
        format_ (Union[None, Unset, str]):
        ocr (Union[None, Unset, str]):
        body (OcrDocumentSyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return sync_detailed(
        client=client,
        body=body,
        format_=format_,
        ocr=ocr,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrDocumentSyncBody,
    format_: Union[None, Unset, str] = UNSET,
    ocr: Union[None, Unset, str] = UNSET,
) -> Response[str]:
    """
    Args:
        format_ (Union[None, Unset, str]):
        ocr (Union[None, Unset, str]):
        body (OcrDocumentSyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        body=body,
        format_=format_,
        ocr=ocr,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: OcrDocumentSyncBody,
    format_: Union[None, Unset, str] = UNSET,
    ocr: Union[None, Unset, str] = UNSET,
) -> Optional[str]:
    """
    Args:
        format_ (Union[None, Unset, str]):
        ocr (Union[None, Unset, str]):
        body (OcrDocumentSyncBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            format_=format_,
            ocr=ocr,
        )
    ).parsed
