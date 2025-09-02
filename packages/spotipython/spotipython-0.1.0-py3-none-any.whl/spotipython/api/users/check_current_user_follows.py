from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.check_current_user_follows_item_type import CheckCurrentUserFollowsItemType
from ...models.check_current_user_follows_response_401 import CheckCurrentUserFollowsResponse401
from ...models.check_current_user_follows_response_403 import CheckCurrentUserFollowsResponse403
from ...models.check_current_user_follows_response_429 import CheckCurrentUserFollowsResponse429
from ...types import UNSET, Response


def _get_kwargs(
    *,
    type_: CheckCurrentUserFollowsItemType,
    ids: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_type_ = type_.value
    params["type"] = json_type_

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/following/contains",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CheckCurrentUserFollowsResponse401,
        CheckCurrentUserFollowsResponse403,
        CheckCurrentUserFollowsResponse429,
        list[bool],
    ]
]:
    if response.status_code == 200:
        response_200 = cast(list[bool], response.json())

        return response_200

    if response.status_code == 401:
        response_401 = CheckCurrentUserFollowsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = CheckCurrentUserFollowsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = CheckCurrentUserFollowsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CheckCurrentUserFollowsResponse401,
        CheckCurrentUserFollowsResponse403,
        CheckCurrentUserFollowsResponse429,
        list[bool],
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
    type_: CheckCurrentUserFollowsItemType,
    ids: str,
) -> Response[
    Union[
        CheckCurrentUserFollowsResponse401,
        CheckCurrentUserFollowsResponse403,
        CheckCurrentUserFollowsResponse429,
        list[bool],
    ]
]:
    """Check If User Follows Artists or Users

     Check to see if the current user is following one or more artists or other Spotify users.

    Args:
        type_ (CheckCurrentUserFollowsItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids) to check. For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckCurrentUserFollowsResponse401, CheckCurrentUserFollowsResponse403, CheckCurrentUserFollowsResponse429, list[bool]]]
    """

    kwargs = _get_kwargs(
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
    type_: CheckCurrentUserFollowsItemType,
    ids: str,
) -> Optional[
    Union[
        CheckCurrentUserFollowsResponse401,
        CheckCurrentUserFollowsResponse403,
        CheckCurrentUserFollowsResponse429,
        list[bool],
    ]
]:
    """Check If User Follows Artists or Users

     Check to see if the current user is following one or more artists or other Spotify users.

    Args:
        type_ (CheckCurrentUserFollowsItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids) to check. For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckCurrentUserFollowsResponse401, CheckCurrentUserFollowsResponse403, CheckCurrentUserFollowsResponse429, list[bool]]
    """

    return sync_detailed(
        client=client,
        type_=type_,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    type_: CheckCurrentUserFollowsItemType,
    ids: str,
) -> Response[
    Union[
        CheckCurrentUserFollowsResponse401,
        CheckCurrentUserFollowsResponse403,
        CheckCurrentUserFollowsResponse429,
        list[bool],
    ]
]:
    """Check If User Follows Artists or Users

     Check to see if the current user is following one or more artists or other Spotify users.

    Args:
        type_ (CheckCurrentUserFollowsItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids) to check. For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckCurrentUserFollowsResponse401, CheckCurrentUserFollowsResponse403, CheckCurrentUserFollowsResponse429, list[bool]]]
    """

    kwargs = _get_kwargs(
        type_=type_,
        ids=ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    type_: CheckCurrentUserFollowsItemType,
    ids: str,
) -> Optional[
    Union[
        CheckCurrentUserFollowsResponse401,
        CheckCurrentUserFollowsResponse403,
        CheckCurrentUserFollowsResponse429,
        list[bool],
    ]
]:
    """Check If User Follows Artists or Users

     Check to see if the current user is following one or more artists or other Spotify users.

    Args:
        type_ (CheckCurrentUserFollowsItemType): The ID type: either `artist` or `user`.
             Example: artist.
        ids (str): A comma-separated list of the artist or the user [Spotify
            IDs](/documentation/web-api/concepts/spotify-uris-ids) to check. For example:
            `ids=74ASZWbe4lXaubB36ztrGX,08td7MxkoHQkXnWAYD8d6Q`. A maximum of 50 IDs can be sent in
            one request.
             Example: 2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckCurrentUserFollowsResponse401, CheckCurrentUserFollowsResponse403, CheckCurrentUserFollowsResponse429, list[bool]]
    """

    return (
        await asyncio_detailed(
            client=client,
            type_=type_,
            ids=ids,
        )
    ).parsed
