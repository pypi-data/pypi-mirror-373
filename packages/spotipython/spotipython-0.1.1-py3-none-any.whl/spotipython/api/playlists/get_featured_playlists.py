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
    locale: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["locale"] = locale

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
    locale: Union[Unset, str] = UNSET,
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
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.
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
        locale=locale,
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
    locale: Union[Unset, str] = UNSET,
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
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.
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
        locale=locale,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    locale: Union[Unset, str] = UNSET,
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
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.
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
        locale=locale,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    locale: Union[Unset, str] = UNSET,
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
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.
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
            locale=locale,
            limit=limit,
            offset=offset,
        )
    ).parsed
