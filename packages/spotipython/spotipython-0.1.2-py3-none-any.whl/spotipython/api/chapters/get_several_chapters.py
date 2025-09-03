from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_several_chapters_response_200 import GetSeveralChaptersResponse200
from ...models.get_several_chapters_response_401 import GetSeveralChaptersResponse401
from ...models.get_several_chapters_response_403 import GetSeveralChaptersResponse403
from ...models.get_several_chapters_response_429 import GetSeveralChaptersResponse429
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
        "url": "/chapters",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetSeveralChaptersResponse200,
        GetSeveralChaptersResponse401,
        GetSeveralChaptersResponse403,
        GetSeveralChaptersResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetSeveralChaptersResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetSeveralChaptersResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetSeveralChaptersResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetSeveralChaptersResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetSeveralChaptersResponse200,
        GetSeveralChaptersResponse401,
        GetSeveralChaptersResponse403,
        GetSeveralChaptersResponse429,
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
        GetSeveralChaptersResponse200,
        GetSeveralChaptersResponse401,
        GetSeveralChaptersResponse403,
        GetSeveralChaptersResponse429,
    ]
]:
    """Get Several Chapters

     Get Spotify catalog information for several audiobook chapters identified by their Spotify IDs.
    Chapters are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU`. Maximum: 50 IDs.
             Example: 0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU,0D5wENdkdwbqlrHoaJ9g29.
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
        Response[Union[GetSeveralChaptersResponse200, GetSeveralChaptersResponse401, GetSeveralChaptersResponse403, GetSeveralChaptersResponse429]]
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
        GetSeveralChaptersResponse200,
        GetSeveralChaptersResponse401,
        GetSeveralChaptersResponse403,
        GetSeveralChaptersResponse429,
    ]
]:
    """Get Several Chapters

     Get Spotify catalog information for several audiobook chapters identified by their Spotify IDs.
    Chapters are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU`. Maximum: 50 IDs.
             Example: 0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU,0D5wENdkdwbqlrHoaJ9g29.
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
        Union[GetSeveralChaptersResponse200, GetSeveralChaptersResponse401, GetSeveralChaptersResponse403, GetSeveralChaptersResponse429]
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
        GetSeveralChaptersResponse200,
        GetSeveralChaptersResponse401,
        GetSeveralChaptersResponse403,
        GetSeveralChaptersResponse429,
    ]
]:
    """Get Several Chapters

     Get Spotify catalog information for several audiobook chapters identified by their Spotify IDs.
    Chapters are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU`. Maximum: 50 IDs.
             Example: 0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU,0D5wENdkdwbqlrHoaJ9g29.
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
        Response[Union[GetSeveralChaptersResponse200, GetSeveralChaptersResponse401, GetSeveralChaptersResponse403, GetSeveralChaptersResponse429]]
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
        GetSeveralChaptersResponse200,
        GetSeveralChaptersResponse401,
        GetSeveralChaptersResponse403,
        GetSeveralChaptersResponse429,
    ]
]:
    """Get Several Chapters

     Get Spotify catalog information for several audiobook chapters identified by their Spotify IDs.
    Chapters are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU`. Maximum: 50 IDs.
             Example: 0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU,0D5wENdkdwbqlrHoaJ9g29.
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
        Union[GetSeveralChaptersResponse200, GetSeveralChaptersResponse401, GetSeveralChaptersResponse403, GetSeveralChaptersResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            market=market,
        )
    ).parsed
