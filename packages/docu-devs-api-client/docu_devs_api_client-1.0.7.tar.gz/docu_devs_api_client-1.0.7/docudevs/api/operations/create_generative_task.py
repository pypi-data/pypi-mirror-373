from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.generative_task_request import GenerativeTaskRequest
from ...models.submit_operation_response import SubmitOperationResponse
from ...types import Response


def _get_kwargs(
    parent_job_id: str,
    *,
    body: GenerativeTaskRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/operation/{parent_job_id}/generative-task",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SubmitOperationResponse]:
    if response.status_code == 200:
        response_200 = SubmitOperationResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SubmitOperationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    parent_job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerativeTaskRequest,
) -> Response[SubmitOperationResponse]:
    """
    Args:
        parent_job_id (str):
        body (GenerativeTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SubmitOperationResponse]
    """

    kwargs = _get_kwargs(
        parent_job_id=parent_job_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    parent_job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerativeTaskRequest,
) -> Optional[SubmitOperationResponse]:
    """
    Args:
        parent_job_id (str):
        body (GenerativeTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SubmitOperationResponse
    """

    return sync_detailed(
        parent_job_id=parent_job_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    parent_job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerativeTaskRequest,
) -> Response[SubmitOperationResponse]:
    """
    Args:
        parent_job_id (str):
        body (GenerativeTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SubmitOperationResponse]
    """

    kwargs = _get_kwargs(
        parent_job_id=parent_job_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    parent_job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: GenerativeTaskRequest,
) -> Optional[SubmitOperationResponse]:
    """
    Args:
        parent_job_id (str):
        body (GenerativeTaskRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SubmitOperationResponse
    """

    return (
        await asyncio_detailed(
            parent_job_id=parent_job_id,
            client=client,
            body=body,
        )
    ).parsed
