from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.save_shows_user_response_401 import SaveShowsUserResponse401
from ...models.save_shows_user_response_403 import SaveShowsUserResponse403
from ...models.save_shows_user_response_429 import SaveShowsUserResponse429
from ...types import UNSET, Response


def _get_kwargs(
    *,
    ids: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/shows",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = SaveShowsUserResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SaveShowsUserResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SaveShowsUserResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]:
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
) -> Response[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]:
    """Save Shows for Current User

     Save one or more shows to current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]
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
) -> Optional[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]:
    """Save Shows for Current User

     Save one or more shows to current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]
    """

    return sync_detailed(
        client=client,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    ids: str,
) -> Response[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]:
    """Save Shows for Current User

     Save one or more shows to current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]
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
) -> Optional[Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]]:
    """Save Shows for Current User

     Save one or more shows to current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveShowsUserResponse401, SaveShowsUserResponse403, SaveShowsUserResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
        )
    ).parsed
