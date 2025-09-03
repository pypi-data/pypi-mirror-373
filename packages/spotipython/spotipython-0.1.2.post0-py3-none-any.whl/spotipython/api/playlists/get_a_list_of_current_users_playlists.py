from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_a_list_of_current_users_playlists_response_401 import GetAListOfCurrentUsersPlaylistsResponse401
from ...models.get_a_list_of_current_users_playlists_response_403 import GetAListOfCurrentUsersPlaylistsResponse403
from ...models.get_a_list_of_current_users_playlists_response_429 import GetAListOfCurrentUsersPlaylistsResponse429
from ...models.paging_playlist_object import PagingPlaylistObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
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
        "url": "/me/playlists",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetAListOfCurrentUsersPlaylistsResponse401,
        GetAListOfCurrentUsersPlaylistsResponse403,
        GetAListOfCurrentUsersPlaylistsResponse429,
        PagingPlaylistObject,
    ]
]:
    if response.status_code == 200:
        response_200 = PagingPlaylistObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetAListOfCurrentUsersPlaylistsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetAListOfCurrentUsersPlaylistsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetAListOfCurrentUsersPlaylistsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetAListOfCurrentUsersPlaylistsResponse401,
        GetAListOfCurrentUsersPlaylistsResponse403,
        GetAListOfCurrentUsersPlaylistsResponse429,
        PagingPlaylistObject,
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
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetAListOfCurrentUsersPlaylistsResponse401,
        GetAListOfCurrentUsersPlaylistsResponse403,
        GetAListOfCurrentUsersPlaylistsResponse429,
        PagingPlaylistObject,
    ]
]:
    r"""Get Current User's Playlists

     Get a list of the playlists owned or followed by the current Spotify
    user.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): 'The index of the first playlist to return. Default:
            0 (the first object). Maximum offset: 100.000\. Use with `limit` to get the
            next set of playlists.'
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAListOfCurrentUsersPlaylistsResponse401, GetAListOfCurrentUsersPlaylistsResponse403, GetAListOfCurrentUsersPlaylistsResponse429, PagingPlaylistObject]]
    """

    kwargs = _get_kwargs(
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
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetAListOfCurrentUsersPlaylistsResponse401,
        GetAListOfCurrentUsersPlaylistsResponse403,
        GetAListOfCurrentUsersPlaylistsResponse429,
        PagingPlaylistObject,
    ]
]:
    r"""Get Current User's Playlists

     Get a list of the playlists owned or followed by the current Spotify
    user.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): 'The index of the first playlist to return. Default:
            0 (the first object). Maximum offset: 100.000\. Use with `limit` to get the
            next set of playlists.'
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAListOfCurrentUsersPlaylistsResponse401, GetAListOfCurrentUsersPlaylistsResponse403, GetAListOfCurrentUsersPlaylistsResponse429, PagingPlaylistObject]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetAListOfCurrentUsersPlaylistsResponse401,
        GetAListOfCurrentUsersPlaylistsResponse403,
        GetAListOfCurrentUsersPlaylistsResponse429,
        PagingPlaylistObject,
    ]
]:
    r"""Get Current User's Playlists

     Get a list of the playlists owned or followed by the current Spotify
    user.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): 'The index of the first playlist to return. Default:
            0 (the first object). Maximum offset: 100.000\. Use with `limit` to get the
            next set of playlists.'
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAListOfCurrentUsersPlaylistsResponse401, GetAListOfCurrentUsersPlaylistsResponse403, GetAListOfCurrentUsersPlaylistsResponse429, PagingPlaylistObject]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetAListOfCurrentUsersPlaylistsResponse401,
        GetAListOfCurrentUsersPlaylistsResponse403,
        GetAListOfCurrentUsersPlaylistsResponse429,
        PagingPlaylistObject,
    ]
]:
    r"""Get Current User's Playlists

     Get a list of the playlists owned or followed by the current Spotify
    user.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): 'The index of the first playlist to return. Default:
            0 (the first object). Maximum offset: 100.000\. Use with `limit` to get the
            next set of playlists.'
             Default: 0. Example: 5.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAListOfCurrentUsersPlaylistsResponse401, GetAListOfCurrentUsersPlaylistsResponse403, GetAListOfCurrentUsersPlaylistsResponse429, PagingPlaylistObject]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
