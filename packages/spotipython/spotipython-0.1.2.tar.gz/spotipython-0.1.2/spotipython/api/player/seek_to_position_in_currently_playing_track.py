from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.seek_to_position_in_currently_playing_track_response_401 import (
    SeekToPositionInCurrentlyPlayingTrackResponse401,
)
from ...models.seek_to_position_in_currently_playing_track_response_403 import (
    SeekToPositionInCurrentlyPlayingTrackResponse403,
)
from ...models.seek_to_position_in_currently_playing_track_response_429 import (
    SeekToPositionInCurrentlyPlayingTrackResponse429,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    position_ms: int,
    device_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["position_ms"] = position_ms

    params["device_id"] = device_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/player/seek",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        Any,
        SeekToPositionInCurrentlyPlayingTrackResponse401,
        SeekToPositionInCurrentlyPlayingTrackResponse403,
        SeekToPositionInCurrentlyPlayingTrackResponse429,
    ]
]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 401:
        response_401 = SeekToPositionInCurrentlyPlayingTrackResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SeekToPositionInCurrentlyPlayingTrackResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SeekToPositionInCurrentlyPlayingTrackResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        Any,
        SeekToPositionInCurrentlyPlayingTrackResponse401,
        SeekToPositionInCurrentlyPlayingTrackResponse403,
        SeekToPositionInCurrentlyPlayingTrackResponse429,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    position_ms: int,
    device_id: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        SeekToPositionInCurrentlyPlayingTrackResponse401,
        SeekToPositionInCurrentlyPlayingTrackResponse403,
        SeekToPositionInCurrentlyPlayingTrackResponse429,
    ]
]:
    """Seek To Position

     Seeks to the given position in the user’s currently playing track. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        position_ms (int): The position in milliseconds to seek to. Must be a
            positive number. Passing in a position that is greater than the length of
            the track will cause the player to start playing the next song.
             Example: 25000.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SeekToPositionInCurrentlyPlayingTrackResponse401, SeekToPositionInCurrentlyPlayingTrackResponse403, SeekToPositionInCurrentlyPlayingTrackResponse429]]
    """

    kwargs = _get_kwargs(
        position_ms=position_ms,
        device_id=device_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    position_ms: int,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        SeekToPositionInCurrentlyPlayingTrackResponse401,
        SeekToPositionInCurrentlyPlayingTrackResponse403,
        SeekToPositionInCurrentlyPlayingTrackResponse429,
    ]
]:
    """Seek To Position

     Seeks to the given position in the user’s currently playing track. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        position_ms (int): The position in milliseconds to seek to. Must be a
            positive number. Passing in a position that is greater than the length of
            the track will cause the player to start playing the next song.
             Example: 25000.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SeekToPositionInCurrentlyPlayingTrackResponse401, SeekToPositionInCurrentlyPlayingTrackResponse403, SeekToPositionInCurrentlyPlayingTrackResponse429]
    """

    return sync_detailed(
        client=client,
        position_ms=position_ms,
        device_id=device_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    position_ms: int,
    device_id: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        SeekToPositionInCurrentlyPlayingTrackResponse401,
        SeekToPositionInCurrentlyPlayingTrackResponse403,
        SeekToPositionInCurrentlyPlayingTrackResponse429,
    ]
]:
    """Seek To Position

     Seeks to the given position in the user’s currently playing track. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        position_ms (int): The position in milliseconds to seek to. Must be a
            positive number. Passing in a position that is greater than the length of
            the track will cause the player to start playing the next song.
             Example: 25000.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SeekToPositionInCurrentlyPlayingTrackResponse401, SeekToPositionInCurrentlyPlayingTrackResponse403, SeekToPositionInCurrentlyPlayingTrackResponse429]]
    """

    kwargs = _get_kwargs(
        position_ms=position_ms,
        device_id=device_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    position_ms: int,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        SeekToPositionInCurrentlyPlayingTrackResponse401,
        SeekToPositionInCurrentlyPlayingTrackResponse403,
        SeekToPositionInCurrentlyPlayingTrackResponse429,
    ]
]:
    """Seek To Position

     Seeks to the given position in the user’s currently playing track. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        position_ms (int): The position in milliseconds to seek to. Must be a
            positive number. Passing in a position that is greater than the length of
            the track will cause the player to start playing the next song.
             Example: 25000.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SeekToPositionInCurrentlyPlayingTrackResponse401, SeekToPositionInCurrentlyPlayingTrackResponse403, SeekToPositionInCurrentlyPlayingTrackResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            position_ms=position_ms,
            device_id=device_id,
        )
    ).parsed
