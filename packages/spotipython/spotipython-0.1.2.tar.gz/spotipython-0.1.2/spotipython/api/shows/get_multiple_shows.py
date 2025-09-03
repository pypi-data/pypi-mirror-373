from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_multiple_shows_response_200 import GetMultipleShowsResponse200
from ...models.get_multiple_shows_response_401 import GetMultipleShowsResponse401
from ...models.get_multiple_shows_response_403 import GetMultipleShowsResponse403
from ...models.get_multiple_shows_response_429 import GetMultipleShowsResponse429
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
        "url": "/shows",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetMultipleShowsResponse200,
        GetMultipleShowsResponse401,
        GetMultipleShowsResponse403,
        GetMultipleShowsResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetMultipleShowsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetMultipleShowsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetMultipleShowsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetMultipleShowsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetMultipleShowsResponse200,
        GetMultipleShowsResponse401,
        GetMultipleShowsResponse403,
        GetMultipleShowsResponse429,
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
        GetMultipleShowsResponse200,
        GetMultipleShowsResponse401,
        GetMultipleShowsResponse403,
        GetMultipleShowsResponse429,
    ]
]:
    """Get Several Shows

     Get Spotify catalog information for several shows based on their Spotify IDs.

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
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleShowsResponse200, GetMultipleShowsResponse401, GetMultipleShowsResponse403, GetMultipleShowsResponse429]]
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
        GetMultipleShowsResponse200,
        GetMultipleShowsResponse401,
        GetMultipleShowsResponse403,
        GetMultipleShowsResponse429,
    ]
]:
    """Get Several Shows

     Get Spotify catalog information for several shows based on their Spotify IDs.

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
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleShowsResponse200, GetMultipleShowsResponse401, GetMultipleShowsResponse403, GetMultipleShowsResponse429]
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
        GetMultipleShowsResponse200,
        GetMultipleShowsResponse401,
        GetMultipleShowsResponse403,
        GetMultipleShowsResponse429,
    ]
]:
    """Get Several Shows

     Get Spotify catalog information for several shows based on their Spotify IDs.

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
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleShowsResponse200, GetMultipleShowsResponse401, GetMultipleShowsResponse403, GetMultipleShowsResponse429]]
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
        GetMultipleShowsResponse200,
        GetMultipleShowsResponse401,
        GetMultipleShowsResponse403,
        GetMultipleShowsResponse429,
    ]
]:
    """Get Several Shows

     Get Spotify catalog information for several shows based on their Spotify IDs.

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
            api/concepts/spotify-uris-ids) for the shows. Maximum: 50 IDs.
             Example: 5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleShowsResponse200, GetMultipleShowsResponse401, GetMultipleShowsResponse403, GetMultipleShowsResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            market=market,
            ids=ids,
        )
    ).parsed
