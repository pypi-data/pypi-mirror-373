from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unfollow_playlist_response_401 import UnfollowPlaylistResponse401
from ...models.unfollow_playlist_response_403 import UnfollowPlaylistResponse403
from ...models.unfollow_playlist_response_429 import UnfollowPlaylistResponse429
from ...types import Response


def _get_kwargs(
    playlist_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/playlists/{playlist_id}/followers",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = UnfollowPlaylistResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = UnfollowPlaylistResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = UnfollowPlaylistResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]:
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
) -> Response[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]:
    """Unfollow Playlist

     Remove the current user as a follower of a playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]:
    """Unfollow Playlist

     Remove the current user as a follower of a playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]
    """

    return sync_detailed(
        playlist_id=playlist_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]:
    """Unfollow Playlist

     Remove the current user as a follower of a playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]]:
    """Unfollow Playlist

     Remove the current user as a follower of a playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UnfollowPlaylistResponse401, UnfollowPlaylistResponse403, UnfollowPlaylistResponse429]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
        )
    ).parsed
