from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_track_response_401 import GetTrackResponse401
from ...models.get_track_response_403 import GetTrackResponse403
from ...models.get_track_response_429 import GetTrackResponse429
from ...models.track_object import TrackObject
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
        "url": f"/tracks/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]:
    if response.status_code == 200:
        response_200 = TrackObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetTrackResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetTrackResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetTrackResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]:
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
) -> Response[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]:
    """Get Track

     Get Spotify catalog information for a single track identified by its
    unique Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.
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
        Response[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]
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
) -> Optional[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]:
    """Get Track

     Get Spotify catalog information for a single track identified by its
    unique Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.
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
        Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]
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
) -> Response[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]:
    """Get Track

     Get Spotify catalog information for a single track identified by its
    unique Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.
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
        Response[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]
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
) -> Optional[Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]]:
    """Get Track

     Get Spotify catalog information for a single track identified by its
    unique Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.
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
        Union[GetTrackResponse401, GetTrackResponse403, GetTrackResponse429, TrackObject]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            market=market,
        )
    ).parsed
