from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_playlist_body import CreatePlaylistBody
from ...models.create_playlist_response_401 import CreatePlaylistResponse401
from ...models.create_playlist_response_403 import CreatePlaylistResponse403
from ...models.create_playlist_response_429 import CreatePlaylistResponse429
from ...models.playlist_object import PlaylistObject
from ...types import Response


def _get_kwargs(
    user_id: str,
    *,
    body: CreatePlaylistBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/users/{user_id}/playlists",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]:
    if response.status_code == 201:
        response_201 = PlaylistObject.from_dict(response.json())

        return response_201

    if response.status_code == 401:
        response_401 = CreatePlaylistResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = CreatePlaylistResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = CreatePlaylistResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: CreatePlaylistBody,
) -> Response[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]:
    """Create Playlist

     Create a playlist for a Spotify user. (The playlist will be empty until
    you [add tracks](/documentation/web-api/reference/add-tracks-to-playlist).)
    Each user is generally limited to a maximum of 11000 playlists.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.
        body (CreatePlaylistBody):  Example: {'name': 'New Playlist', 'description': 'New playlist
            description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: CreatePlaylistBody,
) -> Optional[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]:
    """Create Playlist

     Create a playlist for a Spotify user. (The playlist will be empty until
    you [add tracks](/documentation/web-api/reference/add-tracks-to-playlist).)
    Each user is generally limited to a maximum of 11000 playlists.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.
        body (CreatePlaylistBody):  Example: {'name': 'New Playlist', 'description': 'New playlist
            description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: CreatePlaylistBody,
) -> Response[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]:
    """Create Playlist

     Create a playlist for a Spotify user. (The playlist will be empty until
    you [add tracks](/documentation/web-api/reference/add-tracks-to-playlist).)
    Each user is generally limited to a maximum of 11000 playlists.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.
        body (CreatePlaylistBody):  Example: {'name': 'New Playlist', 'description': 'New playlist
            description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: AuthenticatedClient,
    body: CreatePlaylistBody,
) -> Optional[Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]]:
    """Create Playlist

     Create a playlist for a Spotify user. (The playlist will be empty until
    you [add tracks](/documentation/web-api/reference/add-tracks-to-playlist).)
    Each user is generally limited to a maximum of 11000 playlists.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.
        body (CreatePlaylistBody):  Example: {'name': 'New Playlist', 'description': 'New playlist
            description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreatePlaylistResponse401, CreatePlaylistResponse403, CreatePlaylistResponse429, PlaylistObject]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
