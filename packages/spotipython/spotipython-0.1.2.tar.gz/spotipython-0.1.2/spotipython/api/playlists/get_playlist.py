from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_playlist_response_401 import GetPlaylistResponse401
from ...models.get_playlist_response_403 import GetPlaylistResponse403
from ...models.get_playlist_response_429 import GetPlaylistResponse429
from ...models.playlist_object import PlaylistObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    playlist_id: str,
    *,
    market: Union[Unset, str] = UNSET,
    fields: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["market"] = market

    params["fields"] = fields

    params["additional_types"] = additional_types

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/playlists/{playlist_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]:
    if response.status_code == 200:
        response_200 = PlaylistObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetPlaylistResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetPlaylistResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetPlaylistResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]:
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
    market: Union[Unset, str] = UNSET,
    fields: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Response[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]:
    """Get Playlist

     Get a playlist owned by a Spotify user.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        fields (Union[Unset, str]): Filters for the query: a comma-separated list of the
            fields to return. If omitted, all fields are returned. For example, to get
            just the playlist''s description and URI: `fields=description,uri`. A dot
            separator can be used to specify non-reoccurring fields, while parentheses
            can be used to specify reoccurring fields within objects. For example, to
            get just the added date and user ID of the adder:
            `fields=tracks.items(added_at,added_by.id)`.
            Use multiple parentheses to drill down into nested objects, for example:
            `fields=tracks.items(track(name,href,album(name,href)))`.
            Fields can be excluded by prefixing them with an exclamation mark, for example:
            `fields=tracks.items(track(name,href,album(!name,href)))`
             Example: items(added_by.id,track(name,href,album(name,href))).
        additional_types (Union[Unset, str]): A comma-separated list of item types that your
            client supports besides the default `track` type. Valid types are: `track` and
            `episode`.<br/>
            _**Note**: This parameter was introduced to allow existing clients to maintain their
            current behaviour and might be deprecated in the future._<br/>
            In addition to providing this parameter, make sure that your client properly handles cases
            of new types in the future by checking against the `type` field of each object.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        market=market,
        fields=fields,
        additional_types=additional_types,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    fields: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Optional[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]:
    """Get Playlist

     Get a playlist owned by a Spotify user.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        fields (Union[Unset, str]): Filters for the query: a comma-separated list of the
            fields to return. If omitted, all fields are returned. For example, to get
            just the playlist''s description and URI: `fields=description,uri`. A dot
            separator can be used to specify non-reoccurring fields, while parentheses
            can be used to specify reoccurring fields within objects. For example, to
            get just the added date and user ID of the adder:
            `fields=tracks.items(added_at,added_by.id)`.
            Use multiple parentheses to drill down into nested objects, for example:
            `fields=tracks.items(track(name,href,album(name,href)))`.
            Fields can be excluded by prefixing them with an exclamation mark, for example:
            `fields=tracks.items(track(name,href,album(!name,href)))`
             Example: items(added_by.id,track(name,href,album(name,href))).
        additional_types (Union[Unset, str]): A comma-separated list of item types that your
            client supports besides the default `track` type. Valid types are: `track` and
            `episode`.<br/>
            _**Note**: This parameter was introduced to allow existing clients to maintain their
            current behaviour and might be deprecated in the future._<br/>
            In addition to providing this parameter, make sure that your client properly handles cases
            of new types in the future by checking against the `type` field of each object.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]
    """

    return sync_detailed(
        playlist_id=playlist_id,
        client=client,
        market=market,
        fields=fields,
        additional_types=additional_types,
    ).parsed


async def asyncio_detailed(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    fields: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Response[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]:
    """Get Playlist

     Get a playlist owned by a Spotify user.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        fields (Union[Unset, str]): Filters for the query: a comma-separated list of the
            fields to return. If omitted, all fields are returned. For example, to get
            just the playlist''s description and URI: `fields=description,uri`. A dot
            separator can be used to specify non-reoccurring fields, while parentheses
            can be used to specify reoccurring fields within objects. For example, to
            get just the added date and user ID of the adder:
            `fields=tracks.items(added_at,added_by.id)`.
            Use multiple parentheses to drill down into nested objects, for example:
            `fields=tracks.items(track(name,href,album(name,href)))`.
            Fields can be excluded by prefixing them with an exclamation mark, for example:
            `fields=tracks.items(track(name,href,album(!name,href)))`
             Example: items(added_by.id,track(name,href,album(name,href))).
        additional_types (Union[Unset, str]): A comma-separated list of item types that your
            client supports besides the default `track` type. Valid types are: `track` and
            `episode`.<br/>
            _**Note**: This parameter was introduced to allow existing clients to maintain their
            current behaviour and might be deprecated in the future._<br/>
            In addition to providing this parameter, make sure that your client properly handles cases
            of new types in the future by checking against the `type` field of each object.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]
    """

    kwargs = _get_kwargs(
        playlist_id=playlist_id,
        market=market,
        fields=fields,
        additional_types=additional_types,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    playlist_id: str,
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    fields: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Optional[Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]]:
    """Get Playlist

     Get a playlist owned by a Spotify user.

    Args:
        playlist_id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of
            the playlist.
             Example: 3cEYpjA9oz9GiPac4AsH4n.
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        fields (Union[Unset, str]): Filters for the query: a comma-separated list of the
            fields to return. If omitted, all fields are returned. For example, to get
            just the playlist''s description and URI: `fields=description,uri`. A dot
            separator can be used to specify non-reoccurring fields, while parentheses
            can be used to specify reoccurring fields within objects. For example, to
            get just the added date and user ID of the adder:
            `fields=tracks.items(added_at,added_by.id)`.
            Use multiple parentheses to drill down into nested objects, for example:
            `fields=tracks.items(track(name,href,album(name,href)))`.
            Fields can be excluded by prefixing them with an exclamation mark, for example:
            `fields=tracks.items(track(name,href,album(!name,href)))`
             Example: items(added_by.id,track(name,href,album(name,href))).
        additional_types (Union[Unset, str]): A comma-separated list of item types that your
            client supports besides the default `track` type. Valid types are: `track` and
            `episode`.<br/>
            _**Note**: This parameter was introduced to allow existing clients to maintain their
            current behaviour and might be deprecated in the future._<br/>
            In addition to providing this parameter, make sure that your client properly handles cases
            of new types in the future by checking against the `type` field of each object.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetPlaylistResponse401, GetPlaylistResponse403, GetPlaylistResponse429, PlaylistObject]
    """

    return (
        await asyncio_detailed(
            playlist_id=playlist_id,
            client=client,
            market=market,
            fields=fields,
            additional_types=additional_types,
        )
    ).parsed
