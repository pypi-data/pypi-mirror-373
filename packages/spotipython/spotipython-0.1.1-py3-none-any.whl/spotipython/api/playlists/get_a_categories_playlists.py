from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_a_categories_playlists_response_401 import GetACategoriesPlaylistsResponse401
from ...models.get_a_categories_playlists_response_403 import GetACategoriesPlaylistsResponse403
from ...models.get_a_categories_playlists_response_429 import GetACategoriesPlaylistsResponse429
from ...models.paging_featured_playlist_object import PagingFeaturedPlaylistObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    category_id: str,
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/browse/categories/{category_id}/playlists",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetACategoriesPlaylistsResponse401,
        GetACategoriesPlaylistsResponse403,
        GetACategoriesPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    if response.status_code == 200:
        response_200 = PagingFeaturedPlaylistObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetACategoriesPlaylistsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetACategoriesPlaylistsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetACategoriesPlaylistsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetACategoriesPlaylistsResponse401,
        GetACategoriesPlaylistsResponse403,
        GetACategoriesPlaylistsResponse429,
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
    category_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetACategoriesPlaylistsResponse401,
        GetACategoriesPlaylistsResponse403,
        GetACategoriesPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Category's Playlists

     Get a list of Spotify playlists tagged with a particular category.

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
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
        Response[Union[GetACategoriesPlaylistsResponse401, GetACategoriesPlaylistsResponse403, GetACategoriesPlaylistsResponse429, PagingFeaturedPlaylistObject]]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    category_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetACategoriesPlaylistsResponse401,
        GetACategoriesPlaylistsResponse403,
        GetACategoriesPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Category's Playlists

     Get a list of Spotify playlists tagged with a particular category.

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
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
        Union[GetACategoriesPlaylistsResponse401, GetACategoriesPlaylistsResponse403, GetACategoriesPlaylistsResponse429, PagingFeaturedPlaylistObject]
    """

    return sync_detailed(
        category_id=category_id,
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    category_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetACategoriesPlaylistsResponse401,
        GetACategoriesPlaylistsResponse403,
        GetACategoriesPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Category's Playlists

     Get a list of Spotify playlists tagged with a particular category.

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
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
        Response[Union[GetACategoriesPlaylistsResponse401, GetACategoriesPlaylistsResponse403, GetACategoriesPlaylistsResponse429, PagingFeaturedPlaylistObject]]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    category_id: str,
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetACategoriesPlaylistsResponse401,
        GetACategoriesPlaylistsResponse403,
        GetACategoriesPlaylistsResponse429,
        PagingFeaturedPlaylistObject,
    ]
]:
    """Get Category's Playlists

     Get a list of Spotify playlists tagged with a particular category.

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
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
        Union[GetACategoriesPlaylistsResponse401, GetACategoriesPlaylistsResponse403, GetACategoriesPlaylistsResponse429, PagingFeaturedPlaylistObject]
    """

    return (
        await asyncio_detailed(
            category_id=category_id,
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
