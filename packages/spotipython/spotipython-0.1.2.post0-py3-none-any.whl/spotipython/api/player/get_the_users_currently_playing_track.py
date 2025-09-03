from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.currently_playing_context_object import CurrentlyPlayingContextObject
from ...models.get_the_users_currently_playing_track_response_401 import GetTheUsersCurrentlyPlayingTrackResponse401
from ...models.get_the_users_currently_playing_track_response_403 import GetTheUsersCurrentlyPlayingTrackResponse403
from ...models.get_the_users_currently_playing_track_response_429 import GetTheUsersCurrentlyPlayingTrackResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    market: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["market"] = market

    params["additional_types"] = additional_types

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/player/currently-playing",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CurrentlyPlayingContextObject,
        GetTheUsersCurrentlyPlayingTrackResponse401,
        GetTheUsersCurrentlyPlayingTrackResponse403,
        GetTheUsersCurrentlyPlayingTrackResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = CurrentlyPlayingContextObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetTheUsersCurrentlyPlayingTrackResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetTheUsersCurrentlyPlayingTrackResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetTheUsersCurrentlyPlayingTrackResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CurrentlyPlayingContextObject,
        GetTheUsersCurrentlyPlayingTrackResponse401,
        GetTheUsersCurrentlyPlayingTrackResponse403,
        GetTheUsersCurrentlyPlayingTrackResponse429,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        CurrentlyPlayingContextObject,
        GetTheUsersCurrentlyPlayingTrackResponse401,
        GetTheUsersCurrentlyPlayingTrackResponse403,
        GetTheUsersCurrentlyPlayingTrackResponse429,
    ]
]:
    """Get Currently Playing Track

     Get the object currently being played on the user's Spotify account.

    Args:
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
        Response[Union[CurrentlyPlayingContextObject, GetTheUsersCurrentlyPlayingTrackResponse401, GetTheUsersCurrentlyPlayingTrackResponse403, GetTheUsersCurrentlyPlayingTrackResponse429]]
    """

    kwargs = _get_kwargs(
        market=market,
        additional_types=additional_types,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        CurrentlyPlayingContextObject,
        GetTheUsersCurrentlyPlayingTrackResponse401,
        GetTheUsersCurrentlyPlayingTrackResponse403,
        GetTheUsersCurrentlyPlayingTrackResponse429,
    ]
]:
    """Get Currently Playing Track

     Get the object currently being played on the user's Spotify account.

    Args:
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
        Union[CurrentlyPlayingContextObject, GetTheUsersCurrentlyPlayingTrackResponse401, GetTheUsersCurrentlyPlayingTrackResponse403, GetTheUsersCurrentlyPlayingTrackResponse429]
    """

    return sync_detailed(
        client=client,
        market=market,
        additional_types=additional_types,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        CurrentlyPlayingContextObject,
        GetTheUsersCurrentlyPlayingTrackResponse401,
        GetTheUsersCurrentlyPlayingTrackResponse403,
        GetTheUsersCurrentlyPlayingTrackResponse429,
    ]
]:
    """Get Currently Playing Track

     Get the object currently being played on the user's Spotify account.

    Args:
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
        Response[Union[CurrentlyPlayingContextObject, GetTheUsersCurrentlyPlayingTrackResponse401, GetTheUsersCurrentlyPlayingTrackResponse403, GetTheUsersCurrentlyPlayingTrackResponse429]]
    """

    kwargs = _get_kwargs(
        market=market,
        additional_types=additional_types,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    additional_types: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        CurrentlyPlayingContextObject,
        GetTheUsersCurrentlyPlayingTrackResponse401,
        GetTheUsersCurrentlyPlayingTrackResponse403,
        GetTheUsersCurrentlyPlayingTrackResponse429,
    ]
]:
    """Get Currently Playing Track

     Get the object currently being played on the user's Spotify account.

    Args:
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
        Union[CurrentlyPlayingContextObject, GetTheUsersCurrentlyPlayingTrackResponse401, GetTheUsersCurrentlyPlayingTrackResponse403, GetTheUsersCurrentlyPlayingTrackResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            market=market,
            additional_types=additional_types,
        )
    ).parsed
