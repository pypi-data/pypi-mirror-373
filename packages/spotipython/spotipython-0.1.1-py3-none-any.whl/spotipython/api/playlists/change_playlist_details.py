from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.change_playlist_details_body import ChangePlaylistDetailsBody
from ...models.change_playlist_details_response_401 import ChangePlaylistDetailsResponse401
from ...models.change_playlist_details_response_403 import ChangePlaylistDetailsResponse403
from ...models.change_playlist_details_response_429 import ChangePlaylistDetailsResponse429
from ...types import Response


def _get_kwargs(
    playlist_id: str,
    *,
    body: ChangePlaylistDetailsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/playlists/{playlist_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = ChangePlaylistDetailsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ChangePlaylistDetailsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = ChangePlaylistDetailsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
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
    body: ChangePlaylistDetailsBody,
) -> Response[
    Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
]:
    """Change Playlist Details

     Change a playlist's name and public/private state. (The user must, of
    course, own the playlist.)

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (ChangePlaylistDetailsBody):  Example: {'name': 'Updated Playlist Name',
            'description': 'Updated playlist description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: ChangePlaylistDetailsBody,
) -> Optional[
    Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
]:
    """Change Playlist Details

     Change a playlist's name and public/private state. (The user must, of
    course, own the playlist.)

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (ChangePlaylistDetailsBody):  Example: {'name': 'Updated Playlist Name',
            'description': 'Updated playlist description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
    """

    return sync_detailed(
        playlist_id=playlist_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: ChangePlaylistDetailsBody,
) -> Response[
    Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
]:
    """Change Playlist Details

     Change a playlist's name and public/private state. (The user must, of
    course, own the playlist.)

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (ChangePlaylistDetailsBody):  Example: {'name': 'Updated Playlist Name',
            'description': 'Updated playlist description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: ChangePlaylistDetailsBody,
) -> Optional[
    Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
]:
    """Change Playlist Details

     Change a playlist's name and public/private state. (The user must, of
    course, own the playlist.)

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (ChangePlaylistDetailsBody):  Example: {'name': 'Updated Playlist Name',
            'description': 'Updated playlist description', 'public': False}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ChangePlaylistDetailsResponse401, ChangePlaylistDetailsResponse403, ChangePlaylistDetailsResponse429]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
            body=body,
        )
    ).parsed
