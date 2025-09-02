from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_to_queue_response_401 import AddToQueueResponse401
from ...models.add_to_queue_response_403 import AddToQueueResponse403
from ...models.add_to_queue_response_429 import AddToQueueResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    uri: str,
    device_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["uri"] = uri

    params["device_id"] = device_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/me/player/queue",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 401:
        response_401 = AddToQueueResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AddToQueueResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = AddToQueueResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    uri: str,
    device_id: Union[Unset, str] = UNSET,
) -> Response[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]:
    """Add Item to Playback Queue

     Add an item to be played next in the user's current playback queue. This API only works for users
    who have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        uri (str): The uri of the item to add to the queue. Must be a track or an episode uri.
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]
    """

    kwargs = _get_kwargs(
        uri=uri,
        device_id=device_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    uri: str,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]:
    """Add Item to Playback Queue

     Add an item to be played next in the user's current playback queue. This API only works for users
    who have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        uri (str): The uri of the item to add to the queue. Must be a track or an episode uri.
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]
    """

    return sync_detailed(
        client=client,
        uri=uri,
        device_id=device_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    uri: str,
    device_id: Union[Unset, str] = UNSET,
) -> Response[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]:
    """Add Item to Playback Queue

     Add an item to be played next in the user's current playback queue. This API only works for users
    who have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        uri (str): The uri of the item to add to the queue. Must be a track or an episode uri.
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]
    """

    kwargs = _get_kwargs(
        uri=uri,
        device_id=device_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    uri: str,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]]:
    """Add Item to Playback Queue

     Add an item to be played next in the user's current playback queue. This API only works for users
    who have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        uri (str): The uri of the item to add to the queue. Must be a track or an episode uri.
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AddToQueueResponse401, AddToQueueResponse403, AddToQueueResponse429, Any]
    """

    return (
        await asyncio_detailed(
            client=client,
            uri=uri,
            device_id=device_id,
        )
    ).parsed
