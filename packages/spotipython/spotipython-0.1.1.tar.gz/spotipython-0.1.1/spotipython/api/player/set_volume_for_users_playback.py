from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.set_volume_for_users_playback_response_401 import SetVolumeForUsersPlaybackResponse401
from ...models.set_volume_for_users_playback_response_403 import SetVolumeForUsersPlaybackResponse403
from ...models.set_volume_for_users_playback_response_429 import SetVolumeForUsersPlaybackResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    volume_percent: int,
    device_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["volume_percent"] = volume_percent

    params["device_id"] = device_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/player/volume",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        Any,
        SetVolumeForUsersPlaybackResponse401,
        SetVolumeForUsersPlaybackResponse403,
        SetVolumeForUsersPlaybackResponse429,
    ]
]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 401:
        response_401 = SetVolumeForUsersPlaybackResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SetVolumeForUsersPlaybackResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SetVolumeForUsersPlaybackResponse429.from_dict(response.json())

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
        SetVolumeForUsersPlaybackResponse401,
        SetVolumeForUsersPlaybackResponse403,
        SetVolumeForUsersPlaybackResponse429,
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
    volume_percent: int,
    device_id: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        SetVolumeForUsersPlaybackResponse401,
        SetVolumeForUsersPlaybackResponse403,
        SetVolumeForUsersPlaybackResponse429,
    ]
]:
    """Set Playback Volume

     Set the volume for the user’s current playback device. This API only works for users who have
    Spotify Premium. The order of execution is not guaranteed when you use this API with other Player
    API endpoints.

    Args:
        volume_percent (int): The volume to set. Must be a value from 0 to 100 inclusive.
             Example: 50.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If not
            supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SetVolumeForUsersPlaybackResponse401, SetVolumeForUsersPlaybackResponse403, SetVolumeForUsersPlaybackResponse429]]
    """

    kwargs = _get_kwargs(
        volume_percent=volume_percent,
        device_id=device_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    volume_percent: int,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        SetVolumeForUsersPlaybackResponse401,
        SetVolumeForUsersPlaybackResponse403,
        SetVolumeForUsersPlaybackResponse429,
    ]
]:
    """Set Playback Volume

     Set the volume for the user’s current playback device. This API only works for users who have
    Spotify Premium. The order of execution is not guaranteed when you use this API with other Player
    API endpoints.

    Args:
        volume_percent (int): The volume to set. Must be a value from 0 to 100 inclusive.
             Example: 50.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If not
            supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SetVolumeForUsersPlaybackResponse401, SetVolumeForUsersPlaybackResponse403, SetVolumeForUsersPlaybackResponse429]
    """

    return sync_detailed(
        client=client,
        volume_percent=volume_percent,
        device_id=device_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    volume_percent: int,
    device_id: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        SetVolumeForUsersPlaybackResponse401,
        SetVolumeForUsersPlaybackResponse403,
        SetVolumeForUsersPlaybackResponse429,
    ]
]:
    """Set Playback Volume

     Set the volume for the user’s current playback device. This API only works for users who have
    Spotify Premium. The order of execution is not guaranteed when you use this API with other Player
    API endpoints.

    Args:
        volume_percent (int): The volume to set. Must be a value from 0 to 100 inclusive.
             Example: 50.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If not
            supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SetVolumeForUsersPlaybackResponse401, SetVolumeForUsersPlaybackResponse403, SetVolumeForUsersPlaybackResponse429]]
    """

    kwargs = _get_kwargs(
        volume_percent=volume_percent,
        device_id=device_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    volume_percent: int,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        SetVolumeForUsersPlaybackResponse401,
        SetVolumeForUsersPlaybackResponse403,
        SetVolumeForUsersPlaybackResponse429,
    ]
]:
    """Set Playback Volume

     Set the volume for the user’s current playback device. This API only works for users who have
    Spotify Premium. The order of execution is not guaranteed when you use this API with other Player
    API endpoints.

    Args:
        volume_percent (int): The volume to set. Must be a value from 0 to 100 inclusive.
             Example: 50.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If not
            supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SetVolumeForUsersPlaybackResponse401, SetVolumeForUsersPlaybackResponse403, SetVolumeForUsersPlaybackResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            volume_percent=volume_percent,
            device_id=device_id,
        )
    ).parsed
