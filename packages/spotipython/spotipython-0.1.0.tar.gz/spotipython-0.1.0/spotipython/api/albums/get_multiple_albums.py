from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_multiple_albums_response_200 import GetMultipleAlbumsResponse200
from ...models.get_multiple_albums_response_401 import GetMultipleAlbumsResponse401
from ...models.get_multiple_albums_response_403 import GetMultipleAlbumsResponse403
from ...models.get_multiple_albums_response_429 import GetMultipleAlbumsResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    ids: str,
    market: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["ids"] = ids

    params["market"] = market

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/albums",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetMultipleAlbumsResponse200,
        GetMultipleAlbumsResponse401,
        GetMultipleAlbumsResponse403,
        GetMultipleAlbumsResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetMultipleAlbumsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetMultipleAlbumsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetMultipleAlbumsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetMultipleAlbumsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetMultipleAlbumsResponse200,
        GetMultipleAlbumsResponse401,
        GetMultipleAlbumsResponse403,
        GetMultipleAlbumsResponse429,
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
    market: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        GetMultipleAlbumsResponse200,
        GetMultipleAlbumsResponse401,
        GetMultipleAlbumsResponse403,
        GetMultipleAlbumsResponse429,
    ]
]:
    """Get Several Albums

     Get Spotify catalog information for multiple albums identified by their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
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
            settings](https://www.spotify.com/se/account/overview/).
             Example: ES.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleAlbumsResponse200, GetMultipleAlbumsResponse401, GetMultipleAlbumsResponse403, GetMultipleAlbumsResponse429]]
    """

    kwargs = _get_kwargs(
        ids=ids,
        market=market,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    ids: str,
    market: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        GetMultipleAlbumsResponse200,
        GetMultipleAlbumsResponse401,
        GetMultipleAlbumsResponse403,
        GetMultipleAlbumsResponse429,
    ]
]:
    """Get Several Albums

     Get Spotify catalog information for multiple albums identified by their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
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
            settings](https://www.spotify.com/se/account/overview/).
             Example: ES.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleAlbumsResponse200, GetMultipleAlbumsResponse401, GetMultipleAlbumsResponse403, GetMultipleAlbumsResponse429]
    """

    return sync_detailed(
        client=client,
        ids=ids,
        market=market,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    ids: str,
    market: Union[Unset, str] = UNSET,
) -> Response[
    Union[
        GetMultipleAlbumsResponse200,
        GetMultipleAlbumsResponse401,
        GetMultipleAlbumsResponse403,
        GetMultipleAlbumsResponse429,
    ]
]:
    """Get Several Albums

     Get Spotify catalog information for multiple albums identified by their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
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
            settings](https://www.spotify.com/se/account/overview/).
             Example: ES.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleAlbumsResponse200, GetMultipleAlbumsResponse401, GetMultipleAlbumsResponse403, GetMultipleAlbumsResponse429]]
    """

    kwargs = _get_kwargs(
        ids=ids,
        market=market,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    ids: str,
    market: Union[Unset, str] = UNSET,
) -> Optional[
    Union[
        GetMultipleAlbumsResponse200,
        GetMultipleAlbumsResponse401,
        GetMultipleAlbumsResponse403,
        GetMultipleAlbumsResponse429,
    ]
]:
    """Get Several Albums

     Get Spotify catalog information for multiple albums identified by their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
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
            settings](https://www.spotify.com/se/account/overview/).
             Example: ES.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleAlbumsResponse200, GetMultipleAlbumsResponse401, GetMultipleAlbumsResponse403, GetMultipleAlbumsResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            market=market,
        )
    ).parsed
