from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_users_saved_albums_response_401 import GetUsersSavedAlbumsResponse401
from ...models.get_users_saved_albums_response_403 import GetUsersSavedAlbumsResponse403
from ...models.get_users_saved_albums_response_429 import GetUsersSavedAlbumsResponse429
from ...models.paging_saved_album_object import PagingSavedAlbumObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    market: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["market"] = market

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/albums",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetUsersSavedAlbumsResponse401,
        GetUsersSavedAlbumsResponse403,
        GetUsersSavedAlbumsResponse429,
        PagingSavedAlbumObject,
    ]
]:
    if response.status_code == 200:
        response_200 = PagingSavedAlbumObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetUsersSavedAlbumsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetUsersSavedAlbumsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetUsersSavedAlbumsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetUsersSavedAlbumsResponse401,
        GetUsersSavedAlbumsResponse403,
        GetUsersSavedAlbumsResponse429,
        PagingSavedAlbumObject,
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
    market: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        GetUsersSavedAlbumsResponse401,
        GetUsersSavedAlbumsResponse403,
        GetUsersSavedAlbumsResponse429,
        PagingSavedAlbumObject,
    ]
]:
    """Get User's Saved Albums

     Get a list of the albums saved in the current Spotify user's 'Your Music' library.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.
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
        Response[Union[GetUsersSavedAlbumsResponse401, GetUsersSavedAlbumsResponse403, GetUsersSavedAlbumsResponse429, PagingSavedAlbumObject]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        market=market,
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
    market: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        GetUsersSavedAlbumsResponse401,
        GetUsersSavedAlbumsResponse403,
        GetUsersSavedAlbumsResponse429,
        PagingSavedAlbumObject,
    ]
]:
    """Get User's Saved Albums

     Get a list of the albums saved in the current Spotify user's 'Your Music' library.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.
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
        Union[GetUsersSavedAlbumsResponse401, GetUsersSavedAlbumsResponse403, GetUsersSavedAlbumsResponse429, PagingSavedAlbumObject]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
        market=market,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    market: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        GetUsersSavedAlbumsResponse401,
        GetUsersSavedAlbumsResponse403,
        GetUsersSavedAlbumsResponse429,
        PagingSavedAlbumObject,
    ]
]:
    """Get User's Saved Albums

     Get a list of the albums saved in the current Spotify user's 'Your Music' library.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.
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
        Response[Union[GetUsersSavedAlbumsResponse401, GetUsersSavedAlbumsResponse403, GetUsersSavedAlbumsResponse429, PagingSavedAlbumObject]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        market=market,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    market: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        GetUsersSavedAlbumsResponse401,
        GetUsersSavedAlbumsResponse403,
        GetUsersSavedAlbumsResponse429,
        PagingSavedAlbumObject,
    ]
]:
    """Get User's Saved Albums

     Get a list of the albums saved in the current Spotify user's 'Your Music' library.

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        offset (Union[Unset, int]): The index of the first item to return. Default: 0 (the first
            item). Use with limit to get the next set of items.
             Default: 0. Example: 5.
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
        Union[GetUsersSavedAlbumsResponse401, GetUsersSavedAlbumsResponse403, GetUsersSavedAlbumsResponse429, PagingSavedAlbumObject]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
            market=market,
        )
    ).parsed
