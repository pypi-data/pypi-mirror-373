from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.reorder_or_replace_playlists_tracks_body import ReorderOrReplacePlaylistsTracksBody
from ...models.reorder_or_replace_playlists_tracks_response_200 import ReorderOrReplacePlaylistsTracksResponse200
from ...models.reorder_or_replace_playlists_tracks_response_401 import ReorderOrReplacePlaylistsTracksResponse401
from ...models.reorder_or_replace_playlists_tracks_response_403 import ReorderOrReplacePlaylistsTracksResponse403
from ...models.reorder_or_replace_playlists_tracks_response_429 import ReorderOrReplacePlaylistsTracksResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    playlist_id: str,
    *,
    body: ReorderOrReplacePlaylistsTracksBody,
    uris: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["uris"] = uris

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
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
        ReorderOrReplacePlaylistsTracksResponse200,
        ReorderOrReplacePlaylistsTracksResponse401,
        ReorderOrReplacePlaylistsTracksResponse403,
        ReorderOrReplacePlaylistsTracksResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = ReorderOrReplacePlaylistsTracksResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = ReorderOrReplacePlaylistsTracksResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ReorderOrReplacePlaylistsTracksResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = ReorderOrReplacePlaylistsTracksResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        ReorderOrReplacePlaylistsTracksResponse200,
        ReorderOrReplacePlaylistsTracksResponse401,
        ReorderOrReplacePlaylistsTracksResponse403,
        ReorderOrReplacePlaylistsTracksResponse429,
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
    body: ReorderOrReplacePlaylistsTracksBody,
    uris: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        ReorderOrReplacePlaylistsTracksResponse200,
        ReorderOrReplacePlaylistsTracksResponse401,
        ReorderOrReplacePlaylistsTracksResponse403,
        ReorderOrReplacePlaylistsTracksResponse429,
    ]
]:
    """Update Playlist Items

     Either reorder or replace items in a playlist depending on the request's parameters.
    To reorder items, include `range_start`, `insert_before`, `range_length` and `snapshot_id` in the
    request's body.
    To replace items, include `uris` as either a query parameter or in the request's body.
    Replacing items in a playlist will overwrite its existing items. This operation can be used for
    replacing or clearing items in a playlist.
    <br/>
    **Note**: Replace and reorder are mutually exclusive operations which share the same endpoint, but
    have different parameters.
    These operations can't be applied together in a single request.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to set, can be track or episode URIs. For example: `uris=sp
            otify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M,spotify:episode:51
            2ojhOuo1ktJprKbVcKyQ`<br/>A maximum of 100 items can be set in one request.
        body (ReorderOrReplacePlaylistsTracksBody):  Example: {'range_start': 1, 'insert_before':
            3, 'range_length': 2}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ReorderOrReplacePlaylistsTracksResponse200, ReorderOrReplacePlaylistsTracksResponse401, ReorderOrReplacePlaylistsTracksResponse403, ReorderOrReplacePlaylistsTracksResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        body=body,
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
    body: ReorderOrReplacePlaylistsTracksBody,
    uris: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        ReorderOrReplacePlaylistsTracksResponse200,
        ReorderOrReplacePlaylistsTracksResponse401,
        ReorderOrReplacePlaylistsTracksResponse403,
        ReorderOrReplacePlaylistsTracksResponse429,
    ]
]:
    """Update Playlist Items

     Either reorder or replace items in a playlist depending on the request's parameters.
    To reorder items, include `range_start`, `insert_before`, `range_length` and `snapshot_id` in the
    request's body.
    To replace items, include `uris` as either a query parameter or in the request's body.
    Replacing items in a playlist will overwrite its existing items. This operation can be used for
    replacing or clearing items in a playlist.
    <br/>
    **Note**: Replace and reorder are mutually exclusive operations which share the same endpoint, but
    have different parameters.
    These operations can't be applied together in a single request.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to set, can be track or episode URIs. For example: `uris=sp
            otify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M,spotify:episode:51
            2ojhOuo1ktJprKbVcKyQ`<br/>A maximum of 100 items can be set in one request.
        body (ReorderOrReplacePlaylistsTracksBody):  Example: {'range_start': 1, 'insert_before':
            3, 'range_length': 2}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ReorderOrReplacePlaylistsTracksResponse200, ReorderOrReplacePlaylistsTracksResponse401, ReorderOrReplacePlaylistsTracksResponse403, ReorderOrReplacePlaylistsTracksResponse429]
    """

    return sync_detailed(
        playlist_id=playlist_id,
        client=client,
        body=body,
        uris=uris,
    ).parsed


async def asyncio_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: ReorderOrReplacePlaylistsTracksBody,
    uris: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        ReorderOrReplacePlaylistsTracksResponse200,
        ReorderOrReplacePlaylistsTracksResponse401,
        ReorderOrReplacePlaylistsTracksResponse403,
        ReorderOrReplacePlaylistsTracksResponse429,
    ]
]:
    """Update Playlist Items

     Either reorder or replace items in a playlist depending on the request's parameters.
    To reorder items, include `range_start`, `insert_before`, `range_length` and `snapshot_id` in the
    request's body.
    To replace items, include `uris` as either a query parameter or in the request's body.
    Replacing items in a playlist will overwrite its existing items. This operation can be used for
    replacing or clearing items in a playlist.
    <br/>
    **Note**: Replace and reorder are mutually exclusive operations which share the same endpoint, but
    have different parameters.
    These operations can't be applied together in a single request.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to set, can be track or episode URIs. For example: `uris=sp
            otify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M,spotify:episode:51
            2ojhOuo1ktJprKbVcKyQ`<br/>A maximum of 100 items can be set in one request.
        body (ReorderOrReplacePlaylistsTracksBody):  Example: {'range_start': 1, 'insert_before':
            3, 'range_length': 2}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ReorderOrReplacePlaylistsTracksResponse200, ReorderOrReplacePlaylistsTracksResponse401, ReorderOrReplacePlaylistsTracksResponse403, ReorderOrReplacePlaylistsTracksResponse429]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        body=body,
        uris=uris,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    body: ReorderOrReplacePlaylistsTracksBody,
    uris: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        ReorderOrReplacePlaylistsTracksResponse200,
        ReorderOrReplacePlaylistsTracksResponse401,
        ReorderOrReplacePlaylistsTracksResponse403,
        ReorderOrReplacePlaylistsTracksResponse429,
    ]
]:
    """Update Playlist Items

     Either reorder or replace items in a playlist depending on the request's parameters.
    To reorder items, include `range_start`, `insert_before`, `range_length` and `snapshot_id` in the
    request's body.
    To replace items, include `uris` as either a query parameter or in the request's body.
    Replacing items in a playlist will overwrite its existing items. This operation can be used for
    replacing or clearing items in a playlist.
    <br/>
    **Note**: Replace and reorder are mutually exclusive operations which share the same endpoint, but
    have different parameters.
    These operations can't be applied together in a single request.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        uris (Union[Unset, str]): A comma-separated list of [Spotify URIs](/documentation/web-
            api/concepts/spotify-uris-ids) to set, can be track or episode URIs. For example: `uris=sp
            otify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M,spotify:episode:51
            2ojhOuo1ktJprKbVcKyQ`<br/>A maximum of 100 items can be set in one request.
        body (ReorderOrReplacePlaylistsTracksBody):  Example: {'range_start': 1, 'insert_before':
            3, 'range_length': 2}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ReorderOrReplacePlaylistsTracksResponse200, ReorderOrReplacePlaylistsTracksResponse401, ReorderOrReplacePlaylistsTracksResponse403, ReorderOrReplacePlaylistsTracksResponse429]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
            body=body,
            uris=uris,
        )
    ).parsed
