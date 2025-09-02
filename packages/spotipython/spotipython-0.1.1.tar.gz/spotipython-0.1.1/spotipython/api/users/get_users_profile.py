from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_users_profile_response_401 import GetUsersProfileResponse401
from ...models.get_users_profile_response_403 import GetUsersProfileResponse403
from ...models.get_users_profile_response_429 import GetUsersProfileResponse429
from ...models.public_user_object import PublicUserObject
from ...types import Response


def _get_kwargs(
    user_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/users/{user_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
]:
    if response.status_code == 200:
        response_200 = PublicUserObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetUsersProfileResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetUsersProfileResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetUsersProfileResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
]:
    """Get User's Profile

     Get public profile information about a Spotify user.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
]:
    """Get User's Profile

     Get public profile information about a Spotify user.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
]:
    """Get User's Profile

     Get public profile information about a Spotify user.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
]:
    """Get User's Profile

     Get public profile information about a Spotify user.

    Args:
        user_id (str): The user's [Spotify user ID](/documentation/web-api/concepts/spotify-uris-
            ids).
             Example: smedjan.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetUsersProfileResponse401, GetUsersProfileResponse403, GetUsersProfileResponse429, PublicUserObject]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
        )
    ).parsed
