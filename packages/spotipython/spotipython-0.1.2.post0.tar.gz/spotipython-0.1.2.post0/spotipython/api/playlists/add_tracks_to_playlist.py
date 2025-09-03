from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_tracks_to_playlist_body import AddTracksToPlaylistBody
from ...models.add_tracks_to_playlist_response_201 import AddTracksToPlaylistResponse201
from ...models.add_tracks_to_playlist_response_401 import AddTracksToPlaylistResponse401
from ...models.add_tracks_to_playlist_response_403 import AddTracksToPlaylistResponse403
from ...models.add_tracks_to_playlist_response_429 import AddTracksToPlaylistResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    playlist_id: str,
    *,
    body: AddTracksToPlaylistBody,
    position: Union[Unset, int] = UNSET,
    uris: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["position"] = position

    params["uris"] = uris

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/playlists/{playlist_id}/tracks",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        AddTracksToPlaylistResponse201,
        AddTracksToPlaylistResponse401,
        AddTracksToPlaylistResponse403,
        AddTracksToPlaylistResponse429,
    ]
]:
    if response.status_code == 201:
        response_201 = AddTracksToPlaylistResponse201.from_dict(response.json())

        return response_201

    if response.status_code == 401:
        response_401 = AddTracksToPlaylistResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AddTracksToPlaylistResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = AddTracksToPlaylistResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        AddTracksToPlaylistResponse201,
        AddTracksToPlaylistResponse401,
        AddTracksToPlaylistResponse403,
        AddTracksToPlaylistResponse429,
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
    body: AddTracksToPlaylistBody,
    position: Union[Unset, int] = UNSET,
    uris: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        AddTracksToPlaylistResponse201,
        AddTracksToPlaylistResponse401,
        AddTracksToPlaylistResponse403,
        AddTracksToPlaylistResponse429,
    ]
]:
    """Add Items to Playlist

     Add one or more items to a user's playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        position (Union[Unset, int]): The position to insert the items, a zero-based index. For
            example, to insert the items in the first position: `position=0`; to insert the items in
            the third position: `position=2`. If omitted, the items will be appended to the playlist.
            Items are added in the order they are listed in the query string or request body.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to add, can be track or episode URIs. For
            example:<br/>`uris=spotify:track:4iV5W9uYEdYUVa79Axb7Rh,
            spotify:track:1301WleyT98MSxVHPZCA6M, spotify:episode:512ojhOuo1ktJprKbVcKyQ`<br/>A
            maximum of 100 items can be added in one request. <br/>
            _**Note**: it is likely that passing a large number of item URIs as a query parameter will
            exceed the maximum length of the request URI. When adding a large number of items, it is
            recommended to pass them in the request body, see below._
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M.
        body (AddTracksToPlaylistBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AddTracksToPlaylistResponse201, AddTracksToPlaylistResponse401, AddTracksToPlaylistResponse403, AddTracksToPlaylistResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        body=body,
        position=position,
        uris=uris,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: AddTracksToPlaylistBody,
    position: Union[Unset, int] = UNSET,
    uris: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        AddTracksToPlaylistResponse201,
        AddTracksToPlaylistResponse401,
        AddTracksToPlaylistResponse403,
        AddTracksToPlaylistResponse429,
    ]
]:
    """Add Items to Playlist

     Add one or more items to a user's playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        position (Union[Unset, int]): The position to insert the items, a zero-based index. For
            example, to insert the items in the first position: `position=0`; to insert the items in
            the third position: `position=2`. If omitted, the items will be appended to the playlist.
            Items are added in the order they are listed in the query string or request body.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to add, can be track or episode URIs. For
            example:<br/>`uris=spotify:track:4iV5W9uYEdYUVa79Axb7Rh,
            spotify:track:1301WleyT98MSxVHPZCA6M, spotify:episode:512ojhOuo1ktJprKbVcKyQ`<br/>A
            maximum of 100 items can be added in one request. <br/>
            _**Note**: it is likely that passing a large number of item URIs as a query parameter will
            exceed the maximum length of the request URI. When adding a large number of items, it is
            recommended to pass them in the request body, see below._
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M.
        body (AddTracksToPlaylistBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AddTracksToPlaylistResponse201, AddTracksToPlaylistResponse401, AddTracksToPlaylistResponse403, AddTracksToPlaylistResponse429]
    """

    return sync_detailed(
        playlist_id=playlist_id,
        client=client,
        body=body,
        position=position,
        uris=uris,
    ).parsed


async def asyncio_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: AddTracksToPlaylistBody,
    position: Union[Unset, int] = UNSET,
    uris: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        AddTracksToPlaylistResponse201,
        AddTracksToPlaylistResponse401,
        AddTracksToPlaylistResponse403,
        AddTracksToPlaylistResponse429,
    ]
]:
    """Add Items to Playlist

     Add one or more items to a user's playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        position (Union[Unset, int]): The position to insert the items, a zero-based index. For
            example, to insert the items in the first position: `position=0`; to insert the items in
            the third position: `position=2`. If omitted, the items will be appended to the playlist.
            Items are added in the order they are listed in the query string or request body.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to add, can be track or episode URIs. For
            example:<br/>`uris=spotify:track:4iV5W9uYEdYUVa79Axb7Rh,
            spotify:track:1301WleyT98MSxVHPZCA6M, spotify:episode:512ojhOuo1ktJprKbVcKyQ`<br/>A
            maximum of 100 items can be added in one request. <br/>
            _**Note**: it is likely that passing a large number of item URIs as a query parameter will
            exceed the maximum length of the request URI. When adding a large number of items, it is
            recommended to pass them in the request body, see below._
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M.
        body (AddTracksToPlaylistBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AddTracksToPlaylistResponse201, AddTracksToPlaylistResponse401, AddTracksToPlaylistResponse403, AddTracksToPlaylistResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        body=body,
        position=position,
        uris=uris,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: AddTracksToPlaylistBody,
    position: Union[Unset, int] = UNSET,
    uris: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        AddTracksToPlaylistResponse201,
        AddTracksToPlaylistResponse401,
        AddTracksToPlaylistResponse403,
        AddTracksToPlaylistResponse429,
    ]
]:
    """Add Items to Playlist

     Add one or more items to a user's playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        position (Union[Unset, int]): The position to insert the items, a zero-based index. For
            example, to insert the items in the first position: `position=0`; to insert the items in
            the third position: `position=2`. If omitted, the items will be appended to the playlist.
            Items are added in the order they are listed in the query string or request body.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to add, can be track or episode URIs. For
            example:<br/>`uris=spotify:track:4iV5W9uYEdYUVa79Axb7Rh,
            spotify:track:1301WleyT98MSxVHPZCA6M, spotify:episode:512ojhOuo1ktJprKbVcKyQ`<br/>A
            maximum of 100 items can be added in one request. <br/>
            _**Note**: it is likely that passing a large number of item URIs as a query parameter will
            exceed the maximum length of the request URI. When adding a large number of items, it is
            recommended to pass them in the request body, see below._
             Example: spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M.
        body (AddTracksToPlaylistBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AddTracksToPlaylistResponse201, AddTracksToPlaylistResponse401, AddTracksToPlaylistResponse403, AddTracksToPlaylistResponse429]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
            body=body,
            position=position,
            uris=uris,
        )
    ).parsed
