from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.upload_case_document_legacy_body import UploadCaseDocumentLegacyBody
from ...models.upload_response import UploadResponse
from ...types import Response


def _get_kwargs(
    case_id: int,
    *,
    body: UploadCaseDocumentLegacyBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/cases/{case_id}/upload",
    }

    _kwargs["files"] = body.to_multipart()

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
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadCaseDocumentLegacyBody,
) -> Response[UploadResponse]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentLegacyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        case_id=case_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadCaseDocumentLegacyBody,
) -> Optional[UploadResponse]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentLegacyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return sync_detailed(
        case_id=case_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadCaseDocumentLegacyBody,
) -> Response[UploadResponse]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentLegacyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        case_id=case_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    case_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadCaseDocumentLegacyBody,
) -> Optional[UploadResponse]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentLegacyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return (
        await asyncio_detailed(
            case_id=case_id,
            client=client,
            body=body,
        )
    ).parsed
