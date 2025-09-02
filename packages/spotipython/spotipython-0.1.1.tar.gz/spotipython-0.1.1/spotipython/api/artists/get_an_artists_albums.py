from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_an_artists_albums_response_401 import GetAnArtistsAlbumsResponse401
from ...models.get_an_artists_albums_response_403 import GetAnArtistsAlbumsResponse403
from ...models.get_an_artists_albums_response_429 import GetAnArtistsAlbumsResponse429
from ...models.paging_artist_discography_album_object import PagingArtistDiscographyAlbumObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    include_groups: Union[Unset, str] = UNSET,
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_groups"] = include_groups

    params["market"] = market

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/artists/{id}/albums",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetAnArtistsAlbumsResponse401,
        GetAnArtistsAlbumsResponse403,
        GetAnArtistsAlbumsResponse429,
        PagingArtistDiscographyAlbumObject,
    ]
]:
    if response.status_code == 200:
        response_200 = PagingArtistDiscographyAlbumObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetAnArtistsAlbumsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetAnArtistsAlbumsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetAnArtistsAlbumsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetAnArtistsAlbumsResponse401,
        GetAnArtistsAlbumsResponse403,
        GetAnArtistsAlbumsResponse429,
        PagingArtistDiscographyAlbumObject,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    include_groups: Union[Unset, str] = UNSET,
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetAnArtistsAlbumsResponse401,
        GetAnArtistsAlbumsResponse403,
        GetAnArtistsAlbumsResponse429,
        PagingArtistDiscographyAlbumObject,
    ]
]:
    """Get Artist's Albums

     Get Spotify catalog information about an artist's albums.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
        include_groups (Union[Unset, str]): A comma-separated list of keywords that will be used
            to filter the response. If not supplied, all album types will be returned. <br/>
            Valid values are:<br/>- `album`<br/>- `single`<br/>- `appears_on`<br/>-
            `compilation`<br/>For example: `include_groups=album,single`.
             Example: single,appears_on.
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
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAnArtistsAlbumsResponse401, GetAnArtistsAlbumsResponse403, GetAnArtistsAlbumsResponse429, PagingArtistDiscographyAlbumObject]]
    """

    kwargs = _get_kwargs(
        id=id,
        include_groups=include_groups,
        market=market,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    include_groups: Union[Unset, str] = UNSET,
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetAnArtistsAlbumsResponse401,
        GetAnArtistsAlbumsResponse403,
        GetAnArtistsAlbumsResponse429,
        PagingArtistDiscographyAlbumObject,
    ]
]:
    """Get Artist's Albums

     Get Spotify catalog information about an artist's albums.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
        include_groups (Union[Unset, str]): A comma-separated list of keywords that will be used
            to filter the response. If not supplied, all album types will be returned. <br/>
            Valid values are:<br/>- `album`<br/>- `single`<br/>- `appears_on`<br/>-
            `compilation`<br/>For example: `include_groups=album,single`.
             Example: single,appears_on.
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
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAnArtistsAlbumsResponse401, GetAnArtistsAlbumsResponse403, GetAnArtistsAlbumsResponse429, PagingArtistDiscographyAlbumObject]
    """

    return sync_detailed(
        id=id,
        client=client,
        include_groups=include_groups,
        market=market,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    include_groups: Union[Unset, str] = UNSET,
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetAnArtistsAlbumsResponse401,
        GetAnArtistsAlbumsResponse403,
        GetAnArtistsAlbumsResponse429,
        PagingArtistDiscographyAlbumObject,
    ]
]:
    """Get Artist's Albums

     Get Spotify catalog information about an artist's albums.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
        include_groups (Union[Unset, str]): A comma-separated list of keywords that will be used
            to filter the response. If not supplied, all album types will be returned. <br/>
            Valid values are:<br/>- `album`<br/>- `single`<br/>- `appears_on`<br/>-
            `compilation`<br/>For example: `include_groups=album,single`.
             Example: single,appears_on.
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
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAnArtistsAlbumsResponse401, GetAnArtistsAlbumsResponse403, GetAnArtistsAlbumsResponse429, PagingArtistDiscographyAlbumObject]]
    """

    kwargs = _get_kwargs(
        id=id,
        include_groups=include_groups,
        market=market,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    include_groups: Union[Unset, str] = UNSET,
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetAnArtistsAlbumsResponse401,
        GetAnArtistsAlbumsResponse403,
        GetAnArtistsAlbumsResponse429,
        PagingArtistDiscographyAlbumObject,
    ]
]:
    """Get Artist's Albums

     Get Spotify catalog information about an artist's albums.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
        include_groups (Union[Unset, str]): A comma-separated list of keywords that will be used
            to filter the response. If not supplied, all album types will be returned. <br/>
            Valid values are:<br/>- `album`<br/>- `single`<br/>- `appears_on`<br/>-
            `compilation`<br/>For example: `include_groups=album,single`.
             Example: single,appears_on.
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
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAnArtistsAlbumsResponse401, GetAnArtistsAlbumsResponse403, GetAnArtistsAlbumsResponse429, PagingArtistDiscographyAlbumObject]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            include_groups=include_groups,
            market=market,
            limit=limit,
            offset=offset,
        )
    ).parsed
