from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_multiple_episodes_response_200 import GetMultipleEpisodesResponse200
from ...models.get_multiple_episodes_response_401 import GetMultipleEpisodesResponse401
from ...models.get_multiple_episodes_response_403 import GetMultipleEpisodesResponse403
from ...models.get_multiple_episodes_response_429 import GetMultipleEpisodesResponse429
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
        "url": "/episodes",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetMultipleEpisodesResponse200,
        GetMultipleEpisodesResponse401,
        GetMultipleEpisodesResponse403,
        GetMultipleEpisodesResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetMultipleEpisodesResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetMultipleEpisodesResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetMultipleEpisodesResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetMultipleEpisodesResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetMultipleEpisodesResponse200,
        GetMultipleEpisodesResponse401,
        GetMultipleEpisodesResponse403,
        GetMultipleEpisodesResponse429,
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
        GetMultipleEpisodesResponse200,
        GetMultipleEpisodesResponse401,
        GetMultipleEpisodesResponse403,
        GetMultipleEpisodesResponse429,
    ]
]:
    """Get Several Episodes

     Get Spotify catalog information for several episodes based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the episodes. Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleEpisodesResponse200, GetMultipleEpisodesResponse401, GetMultipleEpisodesResponse403, GetMultipleEpisodesResponse429]]
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
        GetMultipleEpisodesResponse200,
        GetMultipleEpisodesResponse401,
        GetMultipleEpisodesResponse403,
        GetMultipleEpisodesResponse429,
    ]
]:
    """Get Several Episodes

     Get Spotify catalog information for several episodes based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the episodes. Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleEpisodesResponse200, GetMultipleEpisodesResponse401, GetMultipleEpisodesResponse403, GetMultipleEpisodesResponse429]
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
        GetMultipleEpisodesResponse200,
        GetMultipleEpisodesResponse401,
        GetMultipleEpisodesResponse403,
        GetMultipleEpisodesResponse429,
    ]
]:
    """Get Several Episodes

     Get Spotify catalog information for several episodes based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the episodes. Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetMultipleEpisodesResponse200, GetMultipleEpisodesResponse401, GetMultipleEpisodesResponse403, GetMultipleEpisodesResponse429]]
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
        GetMultipleEpisodesResponse200,
        GetMultipleEpisodesResponse401,
        GetMultipleEpisodesResponse403,
        GetMultipleEpisodesResponse429,
    ]
]:
    """Get Several Episodes

     Get Spotify catalog information for several episodes based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the episodes. Maximum: 50 IDs.
             Example: 77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf.
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetMultipleEpisodesResponse200, GetMultipleEpisodesResponse401, GetMultipleEpisodesResponse403, GetMultipleEpisodesResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            market=market,
        )
    ).parsed
