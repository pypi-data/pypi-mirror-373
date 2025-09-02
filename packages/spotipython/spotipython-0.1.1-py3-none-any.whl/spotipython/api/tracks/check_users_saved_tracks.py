from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.check_users_saved_tracks_response_401 import CheckUsersSavedTracksResponse401
from ...models.check_users_saved_tracks_response_403 import CheckUsersSavedTracksResponse403
from ...models.check_users_saved_tracks_response_429 import CheckUsersSavedTracksResponse429
from ...types import UNSET, Response


def _get_kwargs(
    *,
    ids: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/tracks/contains",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]
    ]
]:
    if response.status_code == 200:
        response_200 = cast(list[bool], response.json())

        return response_200

    if response.status_code == 401:
        response_401 = CheckUsersSavedTracksResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = CheckUsersSavedTracksResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = CheckUsersSavedTracksResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]
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
    ids: str,
) -> Response[
    Union[
        CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]
    ]
]:
    """Check User's Saved Tracks

     Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]]]
    """

    kwargs = _get_kwargs(
        ids=ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    ids: str,
) -> Optional[
    Union[
        CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]
    ]
]:
    """Check User's Saved Tracks

     Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]]
    """

    return sync_detailed(
        client=client,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    ids: str,
) -> Response[
    Union[
        CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]
    ]
]:
    """Check User's Saved Tracks

     Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]]]
    """

    kwargs = _get_kwargs(
        ids=ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    ids: str,
) -> Optional[
    Union[
        CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]
    ]
]:
    """Check User's Saved Tracks

     Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckUsersSavedTracksResponse401, CheckUsersSavedTracksResponse403, CheckUsersSavedTracksResponse429, list[bool]]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
        )
    ).parsed
