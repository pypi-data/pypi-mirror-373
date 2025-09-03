from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.generate_schema_body import GenerateSchemaBody
from ...models.upload_response import UploadResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: GenerateSchemaBody,
    instructions_text: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_instructions_text: Union[None, Unset, str]
    if isinstance(instructions_text, Unset):
        json_instructions_text = UNSET
    else:
        json_instructions_text = instructions_text
    params["instructionsText"] = json_instructions_text

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/document/generate-schema",
        "params": params,
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
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerateSchemaBody,
    instructions_text: Union[None, Unset, str] = UNSET,
) -> Response[UploadResponse]:
    """
    Args:
        instructions_text (Union[None, Unset, str]):
        body (GenerateSchemaBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        instructions_text=instructions_text,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerateSchemaBody,
    instructions_text: Union[None, Unset, str] = UNSET,
) -> Optional[UploadResponse]:
    """
    Args:
        instructions_text (Union[None, Unset, str]):
        body (GenerateSchemaBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        instructions_text=instructions_text,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerateSchemaBody,
    instructions_text: Union[None, Unset, str] = UNSET,
) -> Response[UploadResponse]:
    """
    Args:
        instructions_text (Union[None, Unset, str]):
        body (GenerateSchemaBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        instructions_text=instructions_text,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerateSchemaBody,
    instructions_text: Union[None, Unset, str] = UNSET,
) -> Optional[UploadResponse]:
    """
    Args:
        instructions_text (Union[None, Unset, str]):
        body (GenerateSchemaBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            instructions_text=instructions_text,
        )
    ).parsed
