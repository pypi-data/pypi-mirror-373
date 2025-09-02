from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_an_artists_top_tracks_response_200 import GetAnArtistsTopTracksResponse200
from ...models.get_an_artists_top_tracks_response_401 import GetAnArtistsTopTracksResponse401
from ...models.get_an_artists_top_tracks_response_403 import GetAnArtistsTopTracksResponse403
from ...models.get_an_artists_top_tracks_response_429 import GetAnArtistsTopTracksResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    market: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["market"] = market

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/artists/{id}/top-tracks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetAnArtistsTopTracksResponse200,
        GetAnArtistsTopTracksResponse401,
        GetAnArtistsTopTracksResponse403,
        GetAnArtistsTopTracksResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetAnArtistsTopTracksResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetAnArtistsTopTracksResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetAnArtistsTopTracksResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetAnArtistsTopTracksResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetAnArtistsTopTracksResponse200,
        GetAnArtistsTopTracksResponse401,
        GetAnArtistsTopTracksResponse403,
        GetAnArtistsTopTracksResponse429,
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
    market: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        GetAnArtistsTopTracksResponse200,
        GetAnArtistsTopTracksResponse401,
        GetAnArtistsTopTracksResponse403,
        GetAnArtistsTopTracksResponse429,
    ]
]:
    """Get Artist's Top Tracks

     Get Spotify catalog information about an artist's top tracks by country.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAnArtistsTopTracksResponse200, GetAnArtistsTopTracksResponse401, GetAnArtistsTopTracksResponse403, GetAnArtistsTopTracksResponse429]]
    """

    kwargs = _get_kwargs(
        id=id,
        market=market,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        GetAnArtistsTopTracksResponse200,
        GetAnArtistsTopTracksResponse401,
        GetAnArtistsTopTracksResponse403,
        GetAnArtistsTopTracksResponse429,
    ]
]:
    """Get Artist's Top Tracks

     Get Spotify catalog information about an artist's top tracks by country.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAnArtistsTopTracksResponse200, GetAnArtistsTopTracksResponse401, GetAnArtistsTopTracksResponse403, GetAnArtistsTopTracksResponse429]
    """

    return sync_detailed(
        id=id,
        client=client,
        market=market,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        GetAnArtistsTopTracksResponse200,
        GetAnArtistsTopTracksResponse401,
        GetAnArtistsTopTracksResponse403,
        GetAnArtistsTopTracksResponse429,
    ]
]:
    """Get Artist's Top Tracks

     Get Spotify catalog information about an artist's top tracks by country.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAnArtistsTopTracksResponse200, GetAnArtistsTopTracksResponse401, GetAnArtistsTopTracksResponse403, GetAnArtistsTopTracksResponse429]]
    """

    kwargs = _get_kwargs(
        id=id,
        market=market,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        GetAnArtistsTopTracksResponse200,
        GetAnArtistsTopTracksResponse401,
        GetAnArtistsTopTracksResponse403,
        GetAnArtistsTopTracksResponse429,
    ]
]:
    """Get Artist's Top Tracks

     Get Spotify catalog information about an artist's top tracks by country.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAnArtistsTopTracksResponse200, GetAnArtistsTopTracksResponse401, GetAnArtistsTopTracksResponse403, GetAnArtistsTopTracksResponse429]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            market=market,
        )
    ).parsed
