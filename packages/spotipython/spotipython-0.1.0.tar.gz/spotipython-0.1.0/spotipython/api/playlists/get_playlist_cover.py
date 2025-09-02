from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_playlist_cover_response_401 import GetPlaylistCoverResponse401
from ...models.get_playlist_cover_response_403 import GetPlaylistCoverResponse403
from ...models.get_playlist_cover_response_429 import GetPlaylistCoverResponse429
from ...models.image_object import ImageObject
from ...types import Response


def _get_kwargs(
    playlist_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/playlists/{playlist_id}/images",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list["ImageObject"]]
]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ImageObject.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 401:
        response_401 = GetPlaylistCoverResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetPlaylistCoverResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetPlaylistCoverResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list["ImageObject"]]
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
) -> Response[
    Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list["ImageObject"]]
]:
    """Get Playlist Cover Image

     Get the current image associated with a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list['ImageObject']]]
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
) -> Optional[
    Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list["ImageObject"]]
]:
    """Get Playlist Cover Image

     Get the current image associated with a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list['ImageObject']]
    """

    return sync_detailed(
        playlist_id=playlist_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list["ImageObject"]]
]:
    """Get Playlist Cover Image

     Get the current image associated with a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list['ImageObject']]]
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
) -> Optional[
    Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list["ImageObject"]]
]:
    """Get Playlist Cover Image

     Get the current image associated with a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetPlaylistCoverResponse401, GetPlaylistCoverResponse403, GetPlaylistCoverResponse429, list['ImageObject']]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
        )
    ).parsed
