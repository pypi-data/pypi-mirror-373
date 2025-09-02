from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unfollow_artists_users_body import UnfollowArtistsUsersBody
from ...models.unfollow_artists_users_item_type import UnfollowArtistsUsersItemType
from ...models.unfollow_artists_users_response_401 import UnfollowArtistsUsersResponse401
from ...models.unfollow_artists_users_response_403 import UnfollowArtistsUsersResponse403
from ...models.unfollow_artists_users_response_429 import UnfollowArtistsUsersResponse429
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: UnfollowArtistsUsersBody,
    type_: UnfollowArtistsUsersItemType,
    ids: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_type_ = type_.value
    params["type"] = json_type_

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/me/following",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 401:
        response_401 = UnfollowArtistsUsersResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = UnfollowArtistsUsersResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = UnfollowArtistsUsersResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
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
    body: UnfollowArtistsUsersBody,
    type_: UnfollowArtistsUsersItemType,
    ids: str,
) -> Response[
    Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
]:
    """Unfollow Artists or Users

     Remove the current user as a follower of one or more artists or other Spotify users.

    Args:
        type_ (UnfollowArtistsUsersItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids). For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.
        body (UnfollowArtistsUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
        type_=type_,
        ids=ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: UnfollowArtistsUsersBody,
    type_: UnfollowArtistsUsersItemType,
    ids: str,
) -> Optional[
    Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
]:
    """Unfollow Artists or Users

     Remove the current user as a follower of one or more artists or other Spotify users.

    Args:
        type_ (UnfollowArtistsUsersItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids). For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.
        body (UnfollowArtistsUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
    """

    return sync_detailed(
        client=client,
        body=body,
        type_=type_,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: UnfollowArtistsUsersBody,
    type_: UnfollowArtistsUsersItemType,
    ids: str,
) -> Response[
    Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
]:
    """Unfollow Artists or Users

     Remove the current user as a follower of one or more artists or other Spotify users.

    Args:
        type_ (UnfollowArtistsUsersItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids). For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.
        body (UnfollowArtistsUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
        type_=type_,
        ids=ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: UnfollowArtistsUsersBody,
    type_: UnfollowArtistsUsersItemType,
    ids: str,
) -> Optional[
    Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
]:
    """Unfollow Artists or Users

     Remove the current user as a follower of one or more artists or other Spotify users.

    Args:
        type_ (UnfollowArtistsUsersItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids). For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.
        body (UnfollowArtistsUsersBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, UnfollowArtistsUsersResponse401, UnfollowArtistsUsersResponse403, UnfollowArtistsUsersResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            type_=type_,
            ids=ids,
        )
    ).parsed
