from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_followed_item_type import GetFollowedItemType
from ...models.get_followed_response_200 import GetFollowedResponse200
from ...models.get_followed_response_401 import GetFollowedResponse401
from ...models.get_followed_response_403 import GetFollowedResponse403
from ...models.get_followed_response_429 import GetFollowedResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    type_: GetFollowedItemType,
    after: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_type_ = type_.value
    params["type"] = json_type_

    params["after"] = after

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/following",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]:
    if response.status_code == 200:
        response_200 = GetFollowedResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetFollowedResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetFollowedResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetFollowedResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    type_: GetFollowedItemType,
    after: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
) -> Response[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]:
    r"""Get Followed Artists

     Get the current user's followed artists.

    Args:
        type_ (GetFollowedItemType): The ID type: currently only `artist` is supported.
             Example: artist.
        after (Union[Unset, str]): The last artist ID retrieved from the previous request.
             Example: 0I2XqVXqHScXjHhk6AYYRe.
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20\. Minimum:
            1\. Maximum: 50\.
             Default: 20. Example: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]
    """

    kwargs = _get_kwargs(
        type_=type_,
        after=after,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    type_: GetFollowedItemType,
    after: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
) -> Optional[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]:
    r"""Get Followed Artists

     Get the current user's followed artists.

    Args:
        type_ (GetFollowedItemType): The ID type: currently only `artist` is supported.
             Example: artist.
        after (Union[Unset, str]): The last artist ID retrieved from the previous request.
             Example: 0I2XqVXqHScXjHhk6AYYRe.
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20\. Minimum:
            1\. Maximum: 50\.
             Default: 20. Example: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]
    """

    return sync_detailed(
        client=client,
        type_=type_,
        after=after,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    type_: GetFollowedItemType,
    after: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
) -> Response[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]:
    r"""Get Followed Artists

     Get the current user's followed artists.

    Args:
        type_ (GetFollowedItemType): The ID type: currently only `artist` is supported.
             Example: artist.
        after (Union[Unset, str]): The last artist ID retrieved from the previous request.
             Example: 0I2XqVXqHScXjHhk6AYYRe.
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20\. Minimum:
            1\. Maximum: 50\.
             Default: 20. Example: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]
    """

    kwargs = _get_kwargs(
        type_=type_,
        after=after,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    type_: GetFollowedItemType,
    after: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = 20,
) -> Optional[Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]]:
    r"""Get Followed Artists

     Get the current user's followed artists.

    Args:
        type_ (GetFollowedItemType): The ID type: currently only `artist` is supported.
             Example: artist.
        after (Union[Unset, str]): The last artist ID retrieved from the previous request.
             Example: 0I2XqVXqHScXjHhk6AYYRe.
        limit (Union[Unset, int]): The maximum number of items to return. Default: 20\. Minimum:
            1\. Maximum: 50\.
             Default: 20. Example: 10.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetFollowedResponse200, GetFollowedResponse401, GetFollowedResponse403, GetFollowedResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            type_=type_,
            after=after,
            limit=limit,
        )
    ).parsed
