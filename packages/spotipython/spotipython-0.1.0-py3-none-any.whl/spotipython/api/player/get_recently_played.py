from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cursor_paging_play_history_object import CursorPagingPlayHistoryObject
from ...models.get_recently_played_response_401 import GetRecentlyPlayedResponse401
from ...models.get_recently_played_response_403 import GetRecentlyPlayedResponse403
from ...models.get_recently_played_response_429 import GetRecentlyPlayedResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 20,
    after: Union[Unset, int] = UNSET,
    before: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["after"] = after

    params["before"] = before

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/player/recently-played",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CursorPagingPlayHistoryObject,
        GetRecentlyPlayedResponse401,
        GetRecentlyPlayedResponse403,
        GetRecentlyPlayedResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = CursorPagingPlayHistoryObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetRecentlyPlayedResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetRecentlyPlayedResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetRecentlyPlayedResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CursorPagingPlayHistoryObject,
        GetRecentlyPlayedResponse401,
        GetRecentlyPlayedResponse403,
        GetRecentlyPlayedResponse429,
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
    after: Union[Unset, int] = UNSET,
    before: Union[Unset, int] = UNSET,
) -> Response[
    Union[
        CursorPagingPlayHistoryObject,
        GetRecentlyPlayedResponse401,
        GetRecentlyPlayedResponse403,
        GetRecentlyPlayedResponse429,
    ]
]:
    """Get Recently Played Tracks

     Get tracks from the current user's recently played tracks.
    _**Note**: Currently doesn't support podcast episodes._

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        after (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            after (but not including) this cursor position. If `after` is specified, `before`
            must not be specified.
             Example: 1484811043508.
        before (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            before (but not including) this cursor position. If `before` is specified,
            `after` must not be specified.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CursorPagingPlayHistoryObject, GetRecentlyPlayedResponse401, GetRecentlyPlayedResponse403, GetRecentlyPlayedResponse429]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        after=after,
        before=before,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    after: Union[Unset, int] = UNSET,
    before: Union[Unset, int] = UNSET,
) -> Optional[
    Union[
        CursorPagingPlayHistoryObject,
        GetRecentlyPlayedResponse401,
        GetRecentlyPlayedResponse403,
        GetRecentlyPlayedResponse429,
    ]
]:
    """Get Recently Played Tracks

     Get tracks from the current user's recently played tracks.
    _**Note**: Currently doesn't support podcast episodes._

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        after (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            after (but not including) this cursor position. If `after` is specified, `before`
            must not be specified.
             Example: 1484811043508.
        before (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            before (but not including) this cursor position. If `before` is specified,
            `after` must not be specified.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CursorPagingPlayHistoryObject, GetRecentlyPlayedResponse401, GetRecentlyPlayedResponse403, GetRecentlyPlayedResponse429]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        after=after,
        before=before,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    after: Union[Unset, int] = UNSET,
    before: Union[Unset, int] = UNSET,
) -> Response[
    Union[
        CursorPagingPlayHistoryObject,
        GetRecentlyPlayedResponse401,
        GetRecentlyPlayedResponse403,
        GetRecentlyPlayedResponse429,
    ]
]:
    """Get Recently Played Tracks

     Get tracks from the current user's recently played tracks.
    _**Note**: Currently doesn't support podcast episodes._

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        after (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            after (but not including) this cursor position. If `after` is specified, `before`
            must not be specified.
             Example: 1484811043508.
        before (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            before (but not including) this cursor position. If `before` is specified,
            `after` must not be specified.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CursorPagingPlayHistoryObject, GetRecentlyPlayedResponse401, GetRecentlyPlayedResponse403, GetRecentlyPlayedResponse429]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        after=after,
        before=before,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    after: Union[Unset, int] = UNSET,
    before: Union[Unset, int] = UNSET,
) -> Optional[
    Union[
        CursorPagingPlayHistoryObject,
        GetRecentlyPlayedResponse401,
        GetRecentlyPlayedResponse403,
        GetRecentlyPlayedResponse429,
    ]
]:
    """Get Recently Played Tracks

     Get tracks from the current user's recently played tracks.
    _**Note**: Currently doesn't support podcast episodes._

    Args:
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20. Minimum: 1.
            Maximum: 50.
             Default: 20. Example: 10.
        after (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            after (but not including) this cursor position. If `after` is specified, `before`
            must not be specified.
             Example: 1484811043508.
        before (Union[Unset, int]): A Unix timestamp in milliseconds. Returns all items
            before (but not including) this cursor position. If `before` is specified,
            `after` must not be specified.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CursorPagingPlayHistoryObject, GetRecentlyPlayedResponse401, GetRecentlyPlayedResponse403, GetRecentlyPlayedResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            after=after,
            before=before,
        )
    ).parsed
