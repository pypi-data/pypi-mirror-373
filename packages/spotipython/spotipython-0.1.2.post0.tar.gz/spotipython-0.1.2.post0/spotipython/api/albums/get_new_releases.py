from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_new_releases_response_200 import GetNewReleasesResponse200
from ...models.get_new_releases_response_401 import GetNewReleasesResponse401
from ...models.get_new_releases_response_403 import GetNewReleasesResponse403
from ...models.get_new_releases_response_429 import GetNewReleasesResponse429
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
        "url": "/browse/new-releases",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
]:
    if response.status_code == 200:
        response_200 = GetNewReleasesResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetNewReleasesResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetNewReleasesResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetNewReleasesResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
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
    Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
]:
    """Get New Releases

     Get a list of new album releases featured in Spotify (shown, for example, on a Spotify player’s
    “Browse” tab).

    Args:
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
        Response[Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]]
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
    Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
]:
    """Get New Releases

     Get a list of new album releases featured in Spotify (shown, for example, on a Spotify player’s
    “Browse” tab).

    Args:
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
        Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
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
    Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
]:
    """Get New Releases

     Get a list of new album releases featured in Spotify (shown, for example, on a Spotify player’s
    “Browse” tab).

    Args:
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
        Response[Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]]
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
    Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
]:
    """Get New Releases

     Get a list of new album releases featured in Spotify (shown, for example, on a Spotify player’s
    “Browse” tab).

    Args:
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
        Union[GetNewReleasesResponse200, GetNewReleasesResponse401, GetNewReleasesResponse403, GetNewReleasesResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
