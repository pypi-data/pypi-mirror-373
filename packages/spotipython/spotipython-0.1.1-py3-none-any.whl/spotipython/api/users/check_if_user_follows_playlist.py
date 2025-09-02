from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.check_if_user_follows_playlist_response_401 import CheckIfUserFollowsPlaylistResponse401
from ...models.check_if_user_follows_playlist_response_403 import CheckIfUserFollowsPlaylistResponse403
from ...models.check_if_user_follows_playlist_response_429 import CheckIfUserFollowsPlaylistResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    playlist_id: str,
    *,
    ids: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/playlists/{playlist_id}/followers/contains",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CheckIfUserFollowsPlaylistResponse401,
        CheckIfUserFollowsPlaylistResponse403,
        CheckIfUserFollowsPlaylistResponse429,
        list[bool],
    ]
]:
    if response.status_code == 200:
        response_200 = cast(list[bool], response.json())

        return response_200

    if response.status_code == 401:
        response_401 = CheckIfUserFollowsPlaylistResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = CheckIfUserFollowsPlaylistResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = CheckIfUserFollowsPlaylistResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CheckIfUserFollowsPlaylistResponse401,
        CheckIfUserFollowsPlaylistResponse403,
        CheckIfUserFollowsPlaylistResponse429,
        list[bool],
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    ids: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        CheckIfUserFollowsPlaylistResponse401,
        CheckIfUserFollowsPlaylistResponse403,
        CheckIfUserFollowsPlaylistResponse429,
        list[bool],
    ]
]:
    """Check if Current User Follows Playlist

     Check to see if the current user is following a specified playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        ids (Union[Unset, str]): **Deprecated** A single item list containing current user's
            [Spotify Username](/documentation/web-api/concepts/spotify-uris-ids). Maximum: 1 id.
             Example: jmperezperez.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckIfUserFollowsPlaylistResponse401, CheckIfUserFollowsPlaylistResponse403, CheckIfUserFollowsPlaylistResponse429, list[bool]]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        ids=ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    ids: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        CheckIfUserFollowsPlaylistResponse401,
        CheckIfUserFollowsPlaylistResponse403,
        CheckIfUserFollowsPlaylistResponse429,
        list[bool],
    ]
]:
    """Check if Current User Follows Playlist

     Check to see if the current user is following a specified playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        ids (Union[Unset, str]): **Deprecated** A single item list containing current user's
            [Spotify Username](/documentation/web-api/concepts/spotify-uris-ids). Maximum: 1 id.
             Example: jmperezperez.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckIfUserFollowsPlaylistResponse401, CheckIfUserFollowsPlaylistResponse403, CheckIfUserFollowsPlaylistResponse429, list[bool]]
    """

    return sync_detailed(
        playlist_id=playlist_id,
        client=client,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    ids: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        CheckIfUserFollowsPlaylistResponse401,
        CheckIfUserFollowsPlaylistResponse403,
        CheckIfUserFollowsPlaylistResponse429,
        list[bool],
    ]
]:
    """Check if Current User Follows Playlist

     Check to see if the current user is following a specified playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        ids (Union[Unset, str]): **Deprecated** A single item list containing current user's
            [Spotify Username](/documentation/web-api/concepts/spotify-uris-ids). Maximum: 1 id.
             Example: jmperezperez.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckIfUserFollowsPlaylistResponse401, CheckIfUserFollowsPlaylistResponse403, CheckIfUserFollowsPlaylistResponse429, list[bool]]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        ids=ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    ids: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        CheckIfUserFollowsPlaylistResponse401,
        CheckIfUserFollowsPlaylistResponse403,
        CheckIfUserFollowsPlaylistResponse429,
        list[bool],
    ]
]:
    """Check if Current User Follows Playlist

     Check to see if the current user is following a specified playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        ids (Union[Unset, str]): **Deprecated** A single item list containing current user's
            [Spotify Username](/documentation/web-api/concepts/spotify-uris-ids). Maximum: 1 id.
             Example: jmperezperez.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckIfUserFollowsPlaylistResponse401, CheckIfUserFollowsPlaylistResponse403, CheckIfUserFollowsPlaylistResponse429, list[bool]]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
            ids=ids,
        )
    ).parsed
