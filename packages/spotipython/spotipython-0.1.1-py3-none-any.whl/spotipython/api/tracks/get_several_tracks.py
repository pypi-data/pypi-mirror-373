from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_several_tracks_response_200 import GetSeveralTracksResponse200
from ...models.get_several_tracks_response_401 import GetSeveralTracksResponse401
from ...models.get_several_tracks_response_403 import GetSeveralTracksResponse403
from ...models.get_several_tracks_response_429 import GetSeveralTracksResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    market: Union[Unset, str] = UNSET,
    ids: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["market"] = market

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tracks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetSeveralTracksResponse200,
        GetSeveralTracksResponse401,
        GetSeveralTracksResponse403,
        GetSeveralTracksResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetSeveralTracksResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetSeveralTracksResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetSeveralTracksResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetSeveralTracksResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetSeveralTracksResponse200,
        GetSeveralTracksResponse401,
        GetSeveralTracksResponse403,
        GetSeveralTracksResponse429,
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
    market: Union[Unset, str] = UNSET,
    ids: str,
) -> Response[
    Union[
        GetSeveralTracksResponse200,
        GetSeveralTracksResponse401,
        GetSeveralTracksResponse403,
        GetSeveralTracksResponse429,
    ]
]:
    """Get Several Tracks

     Get Spotify catalog information for multiple tracks based on their Spotify IDs.

    Args:
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetSeveralTracksResponse200, GetSeveralTracksResponse401, GetSeveralTracksResponse403, GetSeveralTracksResponse429]]
    """

    kwargs = _get_kwargs(
        market=market,
        ids=ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    ids: str,
) -> Optional[
    Union[
        GetSeveralTracksResponse200,
        GetSeveralTracksResponse401,
        GetSeveralTracksResponse403,
        GetSeveralTracksResponse429,
    ]
]:
    """Get Several Tracks

     Get Spotify catalog information for multiple tracks based on their Spotify IDs.

    Args:
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetSeveralTracksResponse200, GetSeveralTracksResponse401, GetSeveralTracksResponse403, GetSeveralTracksResponse429]
    """

    return sync_detailed(
        client=client,
        market=market,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    ids: str,
) -> Response[
    Union[
        GetSeveralTracksResponse200,
        GetSeveralTracksResponse401,
        GetSeveralTracksResponse403,
        GetSeveralTracksResponse429,
    ]
]:
    """Get Several Tracks

     Get Spotify catalog information for multiple tracks based on their Spotify IDs.

    Args:
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetSeveralTracksResponse200, GetSeveralTracksResponse401, GetSeveralTracksResponse403, GetSeveralTracksResponse429]]
    """

    kwargs = _get_kwargs(
        market=market,
        ids=ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    market: Union[Unset, str] = UNSET,
    ids: str,
) -> Optional[
    Union[
        GetSeveralTracksResponse200,
        GetSeveralTracksResponse401,
        GetSeveralTracksResponse403,
        GetSeveralTracksResponse429,
    ]
]:
    """Get Several Tracks

     Get Spotify catalog information for multiple tracks based on their Spotify IDs.

    Args:
        market (Union[Unset, str]): An [ISO 3166-1 alpha-2 country
            code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
              If a country code is specified, only content that is available in that market will be
            returned.<br/>
              If a valid user access token is specified in the request header, the country associated
            with
              the user account will take priority over this parameter.<br/>
              _**Note**: If neither market or user country are provided, the content is considered
            unavailable for the client._<br/>
              Users can view the country that is associated with their account in the [account
            settings](https://www.spotify.com/account/overview/).
             Example: ES.
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=4iV5W9uYEdYUVa79Axb7Rh,1301WleyT98MSxVHPZCA6M`. Maximum: 50 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetSeveralTracksResponse200, GetSeveralTracksResponse401, GetSeveralTracksResponse403, GetSeveralTracksResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            market=market,
            ids=ids,
        )
    ).parsed
