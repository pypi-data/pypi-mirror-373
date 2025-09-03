from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_queue_response_401 import GetQueueResponse401
from ...models.get_queue_response_403 import GetQueueResponse403
from ...models.get_queue_response_429 import GetQueueResponse429
from ...models.queue_object import QueueObject
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/player/queue",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]:
    if response.status_code == 200:
        response_200 = QueueObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetQueueResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetQueueResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetQueueResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]:
    """Get the User's Queue

     Get the list of objects that make up the user's queue.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]:
    """Get the User's Queue

     Get the list of objects that make up the user's queue.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]:
    """Get the User's Queue

     Get the list of objects that make up the user's queue.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]]:
    """Get the User's Queue

     Get the list of objects that make up the user's queue.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetQueueResponse401, GetQueueResponse403, GetQueueResponse429, QueueObject]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
