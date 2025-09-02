from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.set_repeat_mode_on_users_playback_response_401 import SetRepeatModeOnUsersPlaybackResponse401
from ...models.set_repeat_mode_on_users_playback_response_403 import SetRepeatModeOnUsersPlaybackResponse403
from ...models.set_repeat_mode_on_users_playback_response_429 import SetRepeatModeOnUsersPlaybackResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    state: str,
    device_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["state"] = state

    params["device_id"] = device_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/player/repeat",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        Any,
        SetRepeatModeOnUsersPlaybackResponse401,
        SetRepeatModeOnUsersPlaybackResponse403,
        SetRepeatModeOnUsersPlaybackResponse429,
    ]
]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 401:
        response_401 = SetRepeatModeOnUsersPlaybackResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SetRepeatModeOnUsersPlaybackResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SetRepeatModeOnUsersPlaybackResponse429.from_dict(response.json())

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
        SetRepeatModeOnUsersPlaybackResponse401,
        SetRepeatModeOnUsersPlaybackResponse403,
        SetRepeatModeOnUsersPlaybackResponse429,
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
    state: str,
    device_id: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        SetRepeatModeOnUsersPlaybackResponse401,
        SetRepeatModeOnUsersPlaybackResponse403,
        SetRepeatModeOnUsersPlaybackResponse429,
    ]
]:
    """Set Repeat Mode

     Set the repeat mode for the user's playback. This API only works for users who have Spotify Premium.
    The order of execution is not guaranteed when you use this API with other Player API endpoints.

    Args:
        state (str): **track**, **context** or **off**.<br/>
            **track** will repeat the current track.<br/>
            **context** will repeat the current context.<br/>
            **off** will turn repeat off.
             Example: context.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SetRepeatModeOnUsersPlaybackResponse401, SetRepeatModeOnUsersPlaybackResponse403, SetRepeatModeOnUsersPlaybackResponse429]]
    """

    kwargs = _get_kwargs(
        state=state,
        device_id=device_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    state: str,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        SetRepeatModeOnUsersPlaybackResponse401,
        SetRepeatModeOnUsersPlaybackResponse403,
        SetRepeatModeOnUsersPlaybackResponse429,
    ]
]:
    """Set Repeat Mode

     Set the repeat mode for the user's playback. This API only works for users who have Spotify Premium.
    The order of execution is not guaranteed when you use this API with other Player API endpoints.

    Args:
        state (str): **track**, **context** or **off**.<br/>
            **track** will repeat the current track.<br/>
            **context** will repeat the current context.<br/>
            **off** will turn repeat off.
             Example: context.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SetRepeatModeOnUsersPlaybackResponse401, SetRepeatModeOnUsersPlaybackResponse403, SetRepeatModeOnUsersPlaybackResponse429]
    """

    return sync_detailed(
        client=client,
        state=state,
        device_id=device_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    state: str,
    device_id: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        SetRepeatModeOnUsersPlaybackResponse401,
        SetRepeatModeOnUsersPlaybackResponse403,
        SetRepeatModeOnUsersPlaybackResponse429,
    ]
]:
    """Set Repeat Mode

     Set the repeat mode for the user's playback. This API only works for users who have Spotify Premium.
    The order of execution is not guaranteed when you use this API with other Player API endpoints.

    Args:
        state (str): **track**, **context** or **off**.<br/>
            **track** will repeat the current track.<br/>
            **context** will repeat the current context.<br/>
            **off** will turn repeat off.
             Example: context.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SetRepeatModeOnUsersPlaybackResponse401, SetRepeatModeOnUsersPlaybackResponse403, SetRepeatModeOnUsersPlaybackResponse429]]
    """

    kwargs = _get_kwargs(
        state=state,
        device_id=device_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    state: str,
    device_id: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        SetRepeatModeOnUsersPlaybackResponse401,
        SetRepeatModeOnUsersPlaybackResponse403,
        SetRepeatModeOnUsersPlaybackResponse429,
    ]
]:
    """Set Repeat Mode

     Set the repeat mode for the user's playback. This API only works for users who have Spotify Premium.
    The order of execution is not guaranteed when you use this API with other Player API endpoints.

    Args:
        state (str): **track**, **context** or **off**.<br/>
            **track** will repeat the current track.<br/>
            **context** will repeat the current context.<br/>
            **off** will turn repeat off.
             Example: context.
        device_id (Union[Unset, str]): The id of the device this command is targeting. If
            not supplied, the user's currently active device is the target.
             Example: 0d1841b0976bae2a3a310dd74c0f3df354899bc8.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SetRepeatModeOnUsersPlaybackResponse401, SetRepeatModeOnUsersPlaybackResponse403, SetRepeatModeOnUsersPlaybackResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            state=state,
            device_id=device_id,
        )
    ).parsed
