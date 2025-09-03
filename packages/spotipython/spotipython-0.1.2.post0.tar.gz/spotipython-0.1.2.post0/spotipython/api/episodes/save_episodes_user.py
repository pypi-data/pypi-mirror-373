from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.save_episodes_user_body import SaveEpisodesUserBody
from ...models.save_episodes_user_response_401 import SaveEpisodesUserResponse401
from ...models.save_episodes_user_response_403 import SaveEpisodesUserResponse403
from ...models.save_episodes_user_response_429 import SaveEpisodesUserResponse429
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: SaveEpisodesUserBody,
    ids: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/episodes",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = SaveEpisodesUserResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SaveEpisodesUserResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SaveEpisodesUserResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SaveEpisodesUserBody,
    ids: str,
) -> Response[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]:
    """Save Episodes for Current User

     Save one or more episodes to the current user's library.<br/>
    This API endpoint is in __beta__ and could change without warning. Please share any feedback that
    you have, or issues that you discover, in our [developer community
    forum](https://community.spotify.com/t5/Spotify-for-Developers/bd-p/Spotify_Developer).

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
        body (SaveEpisodesUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
        ids=ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: SaveEpisodesUserBody,
    ids: str,
) -> Optional[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]:
    """Save Episodes for Current User

     Save one or more episodes to the current user's library.<br/>
    This API endpoint is in __beta__ and could change without warning. Please share any feedback that
    you have, or issues that you discover, in our [developer community
    forum](https://community.spotify.com/t5/Spotify-for-Developers/bd-p/Spotify_Developer).

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
        body (SaveEpisodesUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]
    """

    return sync_detailed(
        client=client,
        body=body,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SaveEpisodesUserBody,
    ids: str,
) -> Response[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]:
    """Save Episodes for Current User

     Save one or more episodes to the current user's library.<br/>
    This API endpoint is in __beta__ and could change without warning. Please share any feedback that
    you have, or issues that you discover, in our [developer community
    forum](https://community.spotify.com/t5/Spotify-for-Developers/bd-p/Spotify_Developer).

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
        body (SaveEpisodesUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
        ids=ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SaveEpisodesUserBody,
    ids: str,
) -> Optional[Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]]:
    """Save Episodes for Current User

     Save one or more episodes to the current user's library.<br/>
    This API endpoint is in __beta__ and could change without warning. Please share any feedback that
    you have, or issues that you discover, in our [developer community
    forum](https://community.spotify.com/t5/Spotify-for-Developers/bd-p/Spotify_Developer).

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
        body (SaveEpisodesUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveEpisodesUserResponse401, SaveEpisodesUserResponse403, SaveEpisodesUserResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            ids=ids,
        )
    ).parsed
