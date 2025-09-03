from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_users_top_artists_and_tracks_response_200 import GetUsersTopArtistsAndTracksResponse200
from ...models.get_users_top_artists_and_tracks_response_401 import GetUsersTopArtistsAndTracksResponse401
from ...models.get_users_top_artists_and_tracks_response_403 import GetUsersTopArtistsAndTracksResponse403
from ...models.get_users_top_artists_and_tracks_response_429 import GetUsersTopArtistsAndTracksResponse429
from ...models.get_users_top_artists_and_tracks_type import GetUsersTopArtistsAndTracksType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    type_: GetUsersTopArtistsAndTracksType,
    *,
    time_range: Union[Unset, str] = "medium_term",
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["time_range"] = time_range

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/me/top/{type_}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetUsersTopArtistsAndTracksResponse200,
        GetUsersTopArtistsAndTracksResponse401,
        GetUsersTopArtistsAndTracksResponse403,
        GetUsersTopArtistsAndTracksResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetUsersTopArtistsAndTracksResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetUsersTopArtistsAndTracksResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetUsersTopArtistsAndTracksResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetUsersTopArtistsAndTracksResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetUsersTopArtistsAndTracksResponse200,
        GetUsersTopArtistsAndTracksResponse401,
        GetUsersTopArtistsAndTracksResponse403,
        GetUsersTopArtistsAndTracksResponse429,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    type_: GetUsersTopArtistsAndTracksType,
    *,
    client: AuthenticatedClient,
    time_range: Union[Unset, str] = "medium_term",
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetUsersTopArtistsAndTracksResponse200,
        GetUsersTopArtistsAndTracksResponse401,
        GetUsersTopArtistsAndTracksResponse403,
        GetUsersTopArtistsAndTracksResponse429,
    ]
]:
    """Get User's Top Items

     Get the current user's top artists or tracks based on calculated affinity.

    Args:
        type_ (GetUsersTopArtistsAndTracksType): The type of entity to return. Valid values:
            `artists` or `tracks`
        time_range (Union[Unset, str]): Over what time frame the affinities are computed. Valid
            values: `long_term` (calculated from ~1 year of data and including all new data as it
            becomes available), `medium_term` (approximately last 6 months), `short_term`
            (approximately last 4 weeks). Default: `medium_term`
             Default: 'medium_term'. Example: medium_term.
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
        Response[Union[GetUsersTopArtistsAndTracksResponse200, GetUsersTopArtistsAndTracksResponse401, GetUsersTopArtistsAndTracksResponse403, GetUsersTopArtistsAndTracksResponse429]]
    """

    kwargs = _get_kwargs(
        type_=type_,
        time_range=time_range,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    type_: GetUsersTopArtistsAndTracksType,
    *,
    client: AuthenticatedClient,
    time_range: Union[Unset, str] = "medium_term",
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetUsersTopArtistsAndTracksResponse200,
        GetUsersTopArtistsAndTracksResponse401,
        GetUsersTopArtistsAndTracksResponse403,
        GetUsersTopArtistsAndTracksResponse429,
    ]
]:
    """Get User's Top Items

     Get the current user's top artists or tracks based on calculated affinity.

    Args:
        type_ (GetUsersTopArtistsAndTracksType): The type of entity to return. Valid values:
            `artists` or `tracks`
        time_range (Union[Unset, str]): Over what time frame the affinities are computed. Valid
            values: `long_term` (calculated from ~1 year of data and including all new data as it
            becomes available), `medium_term` (approximately last 6 months), `short_term`
            (approximately last 4 weeks). Default: `medium_term`
             Default: 'medium_term'. Example: medium_term.
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
        Union[GetUsersTopArtistsAndTracksResponse200, GetUsersTopArtistsAndTracksResponse401, GetUsersTopArtistsAndTracksResponse403, GetUsersTopArtistsAndTracksResponse429]
    """

    return sync_detailed(
        type_=type_,
        client=client,
        time_range=time_range,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    type_: GetUsersTopArtistsAndTracksType,
    *,
    client: AuthenticatedClient,
    time_range: Union[Unset, str] = "medium_term",
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Response[
    Union[
        GetUsersTopArtistsAndTracksResponse200,
        GetUsersTopArtistsAndTracksResponse401,
        GetUsersTopArtistsAndTracksResponse403,
        GetUsersTopArtistsAndTracksResponse429,
    ]
]:
    """Get User's Top Items

     Get the current user's top artists or tracks based on calculated affinity.

    Args:
        type_ (GetUsersTopArtistsAndTracksType): The type of entity to return. Valid values:
            `artists` or `tracks`
        time_range (Union[Unset, str]): Over what time frame the affinities are computed. Valid
            values: `long_term` (calculated from ~1 year of data and including all new data as it
            becomes available), `medium_term` (approximately last 6 months), `short_term`
            (approximately last 4 weeks). Default: `medium_term`
             Default: 'medium_term'. Example: medium_term.
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
        Response[Union[GetUsersTopArtistsAndTracksResponse200, GetUsersTopArtistsAndTracksResponse401, GetUsersTopArtistsAndTracksResponse403, GetUsersTopArtistsAndTracksResponse429]]
    """

    kwargs = _get_kwargs(
        type_=type_,
        time_range=time_range,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    type_: GetUsersTopArtistsAndTracksType,
    *,
    client: AuthenticatedClient,
    time_range: Union[Unset, str] = "medium_term",
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
) -> Optional[
    Union[
        GetUsersTopArtistsAndTracksResponse200,
        GetUsersTopArtistsAndTracksResponse401,
        GetUsersTopArtistsAndTracksResponse403,
        GetUsersTopArtistsAndTracksResponse429,
    ]
]:
    """Get User's Top Items

     Get the current user's top artists or tracks based on calculated affinity.

    Args:
        type_ (GetUsersTopArtistsAndTracksType): The type of entity to return. Valid values:
            `artists` or `tracks`
        time_range (Union[Unset, str]): Over what time frame the affinities are computed. Valid
            values: `long_term` (calculated from ~1 year of data and including all new data as it
            becomes available), `medium_term` (approximately last 6 months), `short_term`
            (approximately last 4 weeks). Default: `medium_term`
             Default: 'medium_term'. Example: medium_term.
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
        Union[GetUsersTopArtistsAndTracksResponse200, GetUsersTopArtistsAndTracksResponse401, GetUsersTopArtistsAndTracksResponse403, GetUsersTopArtistsAndTracksResponse429]
    """

    return (
        await asyncio_detailed(
            type_=type_,
            client=client,
            time_range=time_range,
            limit=limit,
            offset=offset,
        )
    ).parsed
