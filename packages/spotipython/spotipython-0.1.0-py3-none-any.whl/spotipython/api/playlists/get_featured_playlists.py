from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_featured_playlists_response_401 import GetFeaturedPlaylistsResponse401
from ...models.get_featured_playlists_response_403 import GetFeaturedPlaylistsResponse403
from ...models.get_featured_playlists_response_429 import GetFeaturedPlaylistsResponse429
from ...models.paging_featured_playlist_object import PagingFeaturedPlaylistObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    country: Union[Unset, str] = UNSET,
    locale: Union[Unset, str] = UNSET,
    timestamp: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["country"] = country

    params["locale"] = locale

    params["timestamp"] = timestamp

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/browse/featured-playlists",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetFeaturedPlaylistsResponse401,
        GetFeaturedPlaylistsResponse403,
        GetFeaturedPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    if response.status_code == 200:
        response_200 = PagingFeaturedPlaylistObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetFeaturedPlaylistsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetFeaturedPlaylistsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetFeaturedPlaylistsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetFeaturedPlaylistsResponse401,
        GetFeaturedPlaylistsResponse403,
        GetFeaturedPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
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
    country: Union[Unset, str] = UNSET,
    locale: Union[Unset, str] = UNSET,
    timestamp: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetFeaturedPlaylistsResponse401,
        GetFeaturedPlaylistsResponse403,
        GetFeaturedPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Featured Playlists

     Get a list of Spotify featured playlists (shown, for example, on a Spotify player's 'Browse' tab).

    Args:
        country (Union[Unset, str]): A country: an [ISO 3166-1 alpha-2 country
            code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). Provide this parameter if you want
            the list of returned items to be relevant to a particular country. If omitted, the
            returned items will be relevant to all countries.
             Example: SE.
        locale (Union[Unset, str]): The desired language, consisting of a lowercase [ISO 639-1
            language code](http://en.wikipedia.org/wiki/ISO_639-1) and an uppercase [ISO 3166-1
            alpha-2 country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an
            underscore. For example: `es_MX`, meaning "Spanish (Mexico)". Provide this parameter if
            you want the results returned in a particular language (where available). <br/>
            _**Note**: if `locale` is not supplied, or if the specified language is not available, all
            strings will be returned in the Spotify default language (American English). The `locale`
            parameter, combined with the `country` parameter, may give odd results if not carefully
            matched. For example `country=SE&locale=de_DE` will return a list of categories relevant
            to Sweden but as German language strings._
             Example: sv_SE.
        timestamp (Union[Unset, str]): A timestamp in [ISO 8601
            format](http://en.wikipedia.org/wiki/ISO_8601): `yyyy-MM-ddTHH:mm:ss`. Use this parameter
            to specify the user's local time to get results tailored for that specific date and time
            in the day. If not provided, the response defaults to the current UTC time. Example:
            "2014-10-23T09:00:00" for a user whose local time is 9AM. If there were no featured
            playlists (or there is no data) at the specified time, the response will revert to the
            current UTC time.
             Example: 2014-10-23 09:00:00.
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
        Response[Union[GetFeaturedPlaylistsResponse401, GetFeaturedPlaylistsResponse403, GetFeaturedPlaylistsResponse429, PagingFeaturedPlaylistObject]]
    """

    kwargs = _get_kwargs(
        country=country,
        locale=locale,
        timestamp=timestamp,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    country: Union[Unset, str] = UNSET,
    locale: Union[Unset, str] = UNSET,
    timestamp: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetFeaturedPlaylistsResponse401,
        GetFeaturedPlaylistsResponse403,
        GetFeaturedPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Featured Playlists

     Get a list of Spotify featured playlists (shown, for example, on a Spotify player's 'Browse' tab).

    Args:
        country (Union[Unset, str]): A country: an [ISO 3166-1 alpha-2 country
            code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). Provide this parameter if you want
            the list of returned items to be relevant to a particular country. If omitted, the
            returned items will be relevant to all countries.
             Example: SE.
        locale (Union[Unset, str]): The desired language, consisting of a lowercase [ISO 639-1
            language code](http://en.wikipedia.org/wiki/ISO_639-1) and an uppercase [ISO 3166-1
            alpha-2 country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an
            underscore. For example: `es_MX`, meaning "Spanish (Mexico)". Provide this parameter if
            you want the results returned in a particular language (where available). <br/>
            _**Note**: if `locale` is not supplied, or if the specified language is not available, all
            strings will be returned in the Spotify default language (American English). The `locale`
            parameter, combined with the `country` parameter, may give odd results if not carefully
            matched. For example `country=SE&locale=de_DE` will return a list of categories relevant
            to Sweden but as German language strings._
             Example: sv_SE.
        timestamp (Union[Unset, str]): A timestamp in [ISO 8601
            format](http://en.wikipedia.org/wiki/ISO_8601): `yyyy-MM-ddTHH:mm:ss`. Use this parameter
            to specify the user's local time to get results tailored for that specific date and time
            in the day. If not provided, the response defaults to the current UTC time. Example:
            "2014-10-23T09:00:00" for a user whose local time is 9AM. If there were no featured
            playlists (or there is no data) at the specified time, the response will revert to the
            current UTC time.
             Example: 2014-10-23 09:00:00.
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
        Union[GetFeaturedPlaylistsResponse401, GetFeaturedPlaylistsResponse403, GetFeaturedPlaylistsResponse429, PagingFeaturedPlaylistObject]
    """

    return sync_detailed(
        client=client,
        country=country,
        locale=locale,
        timestamp=timestamp,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    country: Union[Unset, str] = UNSET,
    locale: Union[Unset, str] = UNSET,
    timestamp: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetFeaturedPlaylistsResponse401,
        GetFeaturedPlaylistsResponse403,
        GetFeaturedPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Featured Playlists

     Get a list of Spotify featured playlists (shown, for example, on a Spotify player's 'Browse' tab).

    Args:
        country (Union[Unset, str]): A country: an [ISO 3166-1 alpha-2 country
            code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). Provide this parameter if you want
            the list of returned items to be relevant to a particular country. If omitted, the
            returned items will be relevant to all countries.
             Example: SE.
        locale (Union[Unset, str]): The desired language, consisting of a lowercase [ISO 639-1
            language code](http://en.wikipedia.org/wiki/ISO_639-1) and an uppercase [ISO 3166-1
            alpha-2 country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an
            underscore. For example: `es_MX`, meaning "Spanish (Mexico)". Provide this parameter if
            you want the results returned in a particular language (where available). <br/>
            _**Note**: if `locale` is not supplied, or if the specified language is not available, all
            strings will be returned in the Spotify default language (American English). The `locale`
            parameter, combined with the `country` parameter, may give odd results if not carefully
            matched. For example `country=SE&locale=de_DE` will return a list of categories relevant
            to Sweden but as German language strings._
             Example: sv_SE.
        timestamp (Union[Unset, str]): A timestamp in [ISO 8601
            format](http://en.wikipedia.org/wiki/ISO_8601): `yyyy-MM-ddTHH:mm:ss`. Use this parameter
            to specify the user's local time to get results tailored for that specific date and time
            in the day. If not provided, the response defaults to the current UTC time. Example:
            "2014-10-23T09:00:00" for a user whose local time is 9AM. If there were no featured
            playlists (or there is no data) at the specified time, the response will revert to the
            current UTC time.
             Example: 2014-10-23 09:00:00.
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
        Response[Union[GetFeaturedPlaylistsResponse401, GetFeaturedPlaylistsResponse403, GetFeaturedPlaylistsResponse429, PagingFeaturedPlaylistObject]]
    """

    kwargs = _get_kwargs(
        country=country,
        locale=locale,
        timestamp=timestamp,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    country: Union[Unset, str] = UNSET,
    locale: Union[Unset, str] = UNSET,
    timestamp: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetFeaturedPlaylistsResponse401,
        GetFeaturedPlaylistsResponse403,
        GetFeaturedPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Featured Playlists

     Get a list of Spotify featured playlists (shown, for example, on a Spotify player's 'Browse' tab).

    Args:
        country (Union[Unset, str]): A country: an [ISO 3166-1 alpha-2 country
            code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). Provide this parameter if you want
            the list of returned items to be relevant to a particular country. If omitted, the
            returned items will be relevant to all countries.
             Example: SE.
        locale (Union[Unset, str]): The desired language, consisting of a lowercase [ISO 639-1
            language code](http://en.wikipedia.org/wiki/ISO_639-1) and an uppercase [ISO 3166-1
            alpha-2 country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an
            underscore. For example: `es_MX`, meaning "Spanish (Mexico)". Provide this parameter if
            you want the results returned in a particular language (where available). <br/>
            _**Note**: if `locale` is not supplied, or if the specified language is not available, all
            strings will be returned in the Spotify default language (American English). The `locale`
            parameter, combined with the `country` parameter, may give odd results if not carefully
            matched. For example `country=SE&locale=de_DE` will return a list of categories relevant
            to Sweden but as German language strings._
             Example: sv_SE.
        timestamp (Union[Unset, str]): A timestamp in [ISO 8601
            format](http://en.wikipedia.org/wiki/ISO_8601): `yyyy-MM-ddTHH:mm:ss`. Use this parameter
            to specify the user's local time to get results tailored for that specific date and time
            in the day. If not provided, the response defaults to the current UTC time. Example:
            "2014-10-23T09:00:00" for a user whose local time is 9AM. If there were no featured
            playlists (or there is no data) at the specified time, the response will revert to the
            current UTC time.
             Example: 2014-10-23 09:00:00.
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
        Union[GetFeaturedPlaylistsResponse401, GetFeaturedPlaylistsResponse403, GetFeaturedPlaylistsResponse429, PagingFeaturedPlaylistObject]
    """

    return (
        await asyncio_detailed(
            client=client,
            country=country,
            locale=locale,
            timestamp=timestamp,
            limit=limit,
            offset=offset,
        )
    ).parsed
