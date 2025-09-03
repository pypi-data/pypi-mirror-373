from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.case_document import CaseDocument
from ...models.upload_case_document_body import UploadCaseDocumentBody
from ...types import Response


def _get_kwargs(
    case_id: int,
    *,
    body: UploadCaseDocumentBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/cases/{case_id}/documents",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[CaseDocument]:
    if response.status_code == 200:
        response_200 = CaseDocument.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[CaseDocument]:
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
    body: UploadCaseDocumentBody,
) -> Response[CaseDocument]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CaseDocument]
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
    body: UploadCaseDocumentBody,
) -> Optional[CaseDocument]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CaseDocument
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
    body: UploadCaseDocumentBody,
) -> Response[CaseDocument]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CaseDocument]
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
    body: UploadCaseDocumentBody,
) -> Optional[CaseDocument]:
    """
    Args:
        case_id (int):
        body (UploadCaseDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CaseDocument
    """

    return (
        await asyncio_detailed(
            case_id=case_id,
            client=client,
            body=body,
        )
    ).parsed
