from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.upload_custom_playlist_cover_response_401 import UploadCustomPlaylistCoverResponse401
from ...models.upload_custom_playlist_cover_response_403 import UploadCustomPlaylistCoverResponse403
from ...models.upload_custom_playlist_cover_response_429 import UploadCustomPlaylistCoverResponse429
from ...types import Response


def _get_kwargs(
    playlist_id: str,
    *,
    body: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/playlists/{playlist_id}/images",
    }

    _kwargs["content"] = body.payload

    headers["Content-Type"] = "image/jpeg"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        Any,
        UploadCustomPlaylistCoverResponse401,
        UploadCustomPlaylistCoverResponse403,
        UploadCustomPlaylistCoverResponse429,
    ]
]:
    if response.status_code == 202:
        response_202 = cast(Any, None)
        return response_202

    if response.status_code == 401:
        response_401 = UploadCustomPlaylistCoverResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = UploadCustomPlaylistCoverResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = UploadCustomPlaylistCoverResponse429.from_dict(response.json())

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
        UploadCustomPlaylistCoverResponse401,
        UploadCustomPlaylistCoverResponse403,
        UploadCustomPlaylistCoverResponse429,
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
    body: str,
) -> Response[
    Union[
        Any,
        UploadCustomPlaylistCoverResponse401,
        UploadCustomPlaylistCoverResponse403,
        UploadCustomPlaylistCoverResponse429,
    ]
]:
    """Add Custom Playlist Cover Image

     Replace the image used to represent a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (str): Base64 encoded JPEG image data, maximum payload size is 256 KB. Example: /9j/2
            wCEABoZGSccJz4lJT5CLy8vQkc9Ozs9R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0c
            BHCcnMyYzPSYmPUc9Mj1HR0dEREdHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//dA
            AQAAf/uAA5BZG9iZQBkwAAAAAH/wAARCAABAAEDACIAAREBAhEB/8QASwABAQAAAAAAAAAAAAAAAAAAAAYBAQAAAAA
            AAAAAAAAAAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAARAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwAAARECEQA/AJgAH//Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UploadCustomPlaylistCoverResponse401, UploadCustomPlaylistCoverResponse403, UploadCustomPlaylistCoverResponse429]]
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
    body: str,
) -> Optional[
    Union[
        Any,
        UploadCustomPlaylistCoverResponse401,
        UploadCustomPlaylistCoverResponse403,
        UploadCustomPlaylistCoverResponse429,
    ]
]:
    """Add Custom Playlist Cover Image

     Replace the image used to represent a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (str): Base64 encoded JPEG image data, maximum payload size is 256 KB. Example: /9j/2
            wCEABoZGSccJz4lJT5CLy8vQkc9Ozs9R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0c
            BHCcnMyYzPSYmPUc9Mj1HR0dEREdHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//dA
            AQAAf/uAA5BZG9iZQBkwAAAAAH/wAARCAABAAEDACIAAREBAhEB/8QASwABAQAAAAAAAAAAAAAAAAAAAAYBAQAAAAA
            AAAAAAAAAAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAARAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwAAARECEQA/AJgAH//Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UploadCustomPlaylistCoverResponse401, UploadCustomPlaylistCoverResponse403, UploadCustomPlaylistCoverResponse429]
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
    body: str,
) -> Response[
    Union[
        Any,
        UploadCustomPlaylistCoverResponse401,
        UploadCustomPlaylistCoverResponse403,
        UploadCustomPlaylistCoverResponse429,
    ]
]:
    """Add Custom Playlist Cover Image

     Replace the image used to represent a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (str): Base64 encoded JPEG image data, maximum payload size is 256 KB. Example: /9j/2
            wCEABoZGSccJz4lJT5CLy8vQkc9Ozs9R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0c
            BHCcnMyYzPSYmPUc9Mj1HR0dEREdHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//dA
            AQAAf/uAA5BZG9iZQBkwAAAAAH/wAARCAABAAEDACIAAREBAhEB/8QASwABAQAAAAAAAAAAAAAAAAAAAAYBAQAAAAA
            AAAAAAAAAAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAARAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwAAARECEQA/AJgAH//Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UploadCustomPlaylistCoverResponse401, UploadCustomPlaylistCoverResponse403, UploadCustomPlaylistCoverResponse429]]
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
    body: str,
) -> Optional[
    Union[
        Any,
        UploadCustomPlaylistCoverResponse401,
        UploadCustomPlaylistCoverResponse403,
        UploadCustomPlaylistCoverResponse429,
    ]
]:
    """Add Custom Playlist Cover Image

     Replace the image used to represent a specific playlist.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        body (str): Base64 encoded JPEG image data, maximum payload size is 256 KB. Example: /9j/2
            wCEABoZGSccJz4lJT5CLy8vQkc9Ozs9R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0c
            BHCcnMyYzPSYmPUc9Mj1HR0dEREdHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//dA
            AQAAf/uAA5BZG9iZQBkwAAAAAH/wAARCAABAAEDACIAAREBAhEB/8QASwABAQAAAAAAAAAAAAAAAAAAAAYBAQAAAAA
            AAAAAAAAAAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAARAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwAAARECEQA/AJgAH//Z.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UploadCustomPlaylistCoverResponse401, UploadCustomPlaylistCoverResponse403, UploadCustomPlaylistCoverResponse429]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
            body=body,
        )
    ).parsed
