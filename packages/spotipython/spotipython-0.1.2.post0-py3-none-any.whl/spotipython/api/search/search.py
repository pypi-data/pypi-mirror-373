from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.search_include_external import SearchIncludeExternal
from ...models.search_response_200 import SearchResponse200
from ...models.search_response_401 import SearchResponse401
from ...models.search_response_403 import SearchResponse403
from ...models.search_response_429 import SearchResponse429
from ...models.search_type_item import SearchTypeItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: str,
    type_: list[SearchTypeItem],
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    include_external: Union[Unset, SearchIncludeExternal] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    json_type_ = []
    for type_item_data in type_:
        type_item = type_item_data.value
        json_type_.append(type_item)

    params["type"] = json_type_

    params["market"] = market

    params["limit"] = limit

    params["offset"] = offset

    json_include_external: Union[Unset, str] = UNSET
    if not isinstance(include_external, Unset):
        json_include_external = include_external.value

    params["include_external"] = json_include_external

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]:
    if response.status_code == 200:
        response_200 = SearchResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = SearchResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SearchResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SearchResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    q: str,
    type_: list[SearchTypeItem],
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    include_external: Union[Unset, SearchIncludeExternal] = UNSET,
) -> Response[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]:
    """Search for Item

     Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or
    audiobooks
    that match a keyword string. Audiobooks are only available within the US, UK, Canada, Ireland, New
    Zealand and Australia markets.

    Args:
        q (str): Your search query.

            You can narrow down your search using field filters. The available filters are `album`,
            `artist`, `track`, `year`, `upc`, `tag:hipster`, `tag:new`, `isrc`, and `genre`. Each
            field filter only applies to certain result types.

            The `artist` and `year` filters can be used while searching albums, artists and tracks.
            You can filter on a single `year` or a range (e.g. 1955-1960).<br />
            The `album` filter can be used while searching albums and tracks.<br />
            The `genre` filter can be used while searching artists and tracks.<br />
            The `isrc` and `track` filters can be used while searching tracks.<br />
            The `upc`, `tag:new` and `tag:hipster` filters can only be used while searching albums.
            The `tag:new` filter will return albums released in the past two weeks and `tag:hipster`
            can be used to return only albums with the lowest 10% popularity.<br />
             Example: remaster%20track:Doxy%20artist:Miles%20Davis.
        type_ (list[SearchTypeItem]): A comma-separated list of item types to search across.
            Search results include hits
            from all the specified item types. For example: `q=abacab&type=album,track` returns
            both albums and tracks matching "abacab".
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
        limit (Union[Unset, int]): The maximum number of results to return in each item type.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first result to return. Use
            with limit to get the next page of search results.
             Default: 0. Example: 5.
        include_external (Union[Unset, SearchIncludeExternal]): If `include_external=audio` is
            specified it signals that the client can play externally hosted audio content, and marks
            the content as playable in the response. By default externally hosted audio content is
            marked as unplayable in the response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]
    """

    kwargs = _get_kwargs(
        q=q,
        type_=type_,
        market=market,
        limit=limit,
        offset=offset,
        include_external=include_external,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    q: str,
    type_: list[SearchTypeItem],
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    include_external: Union[Unset, SearchIncludeExternal] = UNSET,
) -> Optional[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]:
    """Search for Item

     Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or
    audiobooks
    that match a keyword string. Audiobooks are only available within the US, UK, Canada, Ireland, New
    Zealand and Australia markets.

    Args:
        q (str): Your search query.

            You can narrow down your search using field filters. The available filters are `album`,
            `artist`, `track`, `year`, `upc`, `tag:hipster`, `tag:new`, `isrc`, and `genre`. Each
            field filter only applies to certain result types.

            The `artist` and `year` filters can be used while searching albums, artists and tracks.
            You can filter on a single `year` or a range (e.g. 1955-1960).<br />
            The `album` filter can be used while searching albums and tracks.<br />
            The `genre` filter can be used while searching artists and tracks.<br />
            The `isrc` and `track` filters can be used while searching tracks.<br />
            The `upc`, `tag:new` and `tag:hipster` filters can only be used while searching albums.
            The `tag:new` filter will return albums released in the past two weeks and `tag:hipster`
            can be used to return only albums with the lowest 10% popularity.<br />
             Example: remaster%20track:Doxy%20artist:Miles%20Davis.
        type_ (list[SearchTypeItem]): A comma-separated list of item types to search across.
            Search results include hits
            from all the specified item types. For example: `q=abacab&type=album,track` returns
            both albums and tracks matching "abacab".
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
        limit (Union[Unset, int]): The maximum number of results to return in each item type.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first result to return. Use
            with limit to get the next page of search results.
             Default: 0. Example: 5.
        include_external (Union[Unset, SearchIncludeExternal]): If `include_external=audio` is
            specified it signals that the client can play externally hosted audio content, and marks
            the content as playable in the response. By default externally hosted audio content is
            marked as unplayable in the response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]
    """

    return sync_detailed(
        client=client,
        q=q,
        type_=type_,
        market=market,
        limit=limit,
        offset=offset,
        include_external=include_external,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    q: str,
    type_: list[SearchTypeItem],
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    include_external: Union[Unset, SearchIncludeExternal] = UNSET,
) -> Response[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]:
    """Search for Item

     Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or
    audiobooks
    that match a keyword string. Audiobooks are only available within the US, UK, Canada, Ireland, New
    Zealand and Australia markets.

    Args:
        q (str): Your search query.

            You can narrow down your search using field filters. The available filters are `album`,
            `artist`, `track`, `year`, `upc`, `tag:hipster`, `tag:new`, `isrc`, and `genre`. Each
            field filter only applies to certain result types.

            The `artist` and `year` filters can be used while searching albums, artists and tracks.
            You can filter on a single `year` or a range (e.g. 1955-1960).<br />
            The `album` filter can be used while searching albums and tracks.<br />
            The `genre` filter can be used while searching artists and tracks.<br />
            The `isrc` and `track` filters can be used while searching tracks.<br />
            The `upc`, `tag:new` and `tag:hipster` filters can only be used while searching albums.
            The `tag:new` filter will return albums released in the past two weeks and `tag:hipster`
            can be used to return only albums with the lowest 10% popularity.<br />
             Example: remaster%20track:Doxy%20artist:Miles%20Davis.
        type_ (list[SearchTypeItem]): A comma-separated list of item types to search across.
            Search results include hits
            from all the specified item types. For example: `q=abacab&type=album,track` returns
            both albums and tracks matching "abacab".
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
        limit (Union[Unset, int]): The maximum number of results to return in each item type.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first result to return. Use
            with limit to get the next page of search results.
             Default: 0. Example: 5.
        include_external (Union[Unset, SearchIncludeExternal]): If `include_external=audio` is
            specified it signals that the client can play externally hosted audio content, and marks
            the content as playable in the response. By default externally hosted audio content is
            marked as unplayable in the response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]
    """

    kwargs = _get_kwargs(
        q=q,
        type_=type_,
        market=market,
        limit=limit,
        offset=offset,
        include_external=include_external,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    q: str,
    type_: list[SearchTypeItem],
    market: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    include_external: Union[Unset, SearchIncludeExternal] = UNSET,
) -> Optional[Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]]:
    """Search for Item

     Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or
    audiobooks
    that match a keyword string. Audiobooks are only available within the US, UK, Canada, Ireland, New
    Zealand and Australia markets.

    Args:
        q (str): Your search query.

            You can narrow down your search using field filters. The available filters are `album`,
            `artist`, `track`, `year`, `upc`, `tag:hipster`, `tag:new`, `isrc`, and `genre`. Each
            field filter only applies to certain result types.

            The `artist` and `year` filters can be used while searching albums, artists and tracks.
            You can filter on a single `year` or a range (e.g. 1955-1960).<br />
            The `album` filter can be used while searching albums and tracks.<br />
            The `genre` filter can be used while searching artists and tracks.<br />
            The `isrc` and `track` filters can be used while searching tracks.<br />
            The `upc`, `tag:new` and `tag:hipster` filters can only be used while searching albums.
            The `tag:new` filter will return albums released in the past two weeks and `tag:hipster`
            can be used to return only albums with the lowest 10% popularity.<br />
             Example: remaster%20track:Doxy%20artist:Miles%20Davis.
        type_ (list[SearchTypeItem]): A comma-separated list of item types to search across.
            Search results include hits
            from all the specified item types. For example: `q=abacab&type=album,track` returns
            both albums and tracks matching "abacab".
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
        limit (Union[Unset, int]): The maximum number of results to return in each item type.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first result to return. Use
            with limit to get the next page of search results.
             Default: 0. Example: 5.
        include_external (Union[Unset, SearchIncludeExternal]): If `include_external=audio` is
            specified it signals that the client can play externally hosted audio content, and marks
            the content as playable in the response. By default externally hosted audio content is
            marked as unplayable in the response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[SearchResponse200, SearchResponse401, SearchResponse403, SearchResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            type_=type_,
            market=market,
            limit=limit,
            offset=offset,
            include_external=include_external,
        )
    ).parsed
