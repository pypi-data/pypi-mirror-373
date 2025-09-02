from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_multiple_audiobooks_response_200 import GetMultipleAudiobooksResponse200
from ...models.get_multiple_audiobooks_response_401 import GetMultipleAudiobooksResponse401
from ...models.get_multiple_audiobooks_response_403 import GetMultipleAudiobooksResponse403
from ...models.get_multiple_audiobooks_response_429 import GetMultipleAudiobooksResponse429
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
        "url": "/audiobooks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetMultipleAudiobooksResponse200,
        GetMultipleAudiobooksResponse401,
        GetMultipleAudiobooksResponse403,
        GetMultipleAudiobooksResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetMultipleAudiobooksResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetMultipleAudiobooksResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetMultipleAudiobooksResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetMultipleAudiobooksResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetMultipleAudiobooksResponse200,
        GetMultipleAudiobooksResponse401,
        GetMultipleAudiobooksResponse403,
        GetMultipleAudiobooksResponse429,
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
        GetMultipleAudiobooksResponse200,
        GetMultipleAudiobooksResponse401,
        GetMultipleAudiobooksResponse403,
        GetMultipleAudiobooksResponse429,
    ]
]:
    """Get Several Audiobooks

     Get Spotify catalog information for several audiobooks identified by their Spotify IDs. Audiobooks
    are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.
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
        Response[Union[GetMultipleAudiobooksResponse200, GetMultipleAudiobooksResponse401, GetMultipleAudiobooksResponse403, GetMultipleAudiobooksResponse429]]
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
        GetMultipleAudiobooksResponse200,
        GetMultipleAudiobooksResponse401,
        GetMultipleAudiobooksResponse403,
        GetMultipleAudiobooksResponse429,
    ]
]:
    """Get Several Audiobooks

     Get Spotify catalog information for several audiobooks identified by their Spotify IDs. Audiobooks
    are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.
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
        Union[GetMultipleAudiobooksResponse200, GetMultipleAudiobooksResponse401, GetMultipleAudiobooksResponse403, GetMultipleAudiobooksResponse429]
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
        GetMultipleAudiobooksResponse200,
        GetMultipleAudiobooksResponse401,
        GetMultipleAudiobooksResponse403,
        GetMultipleAudiobooksResponse429,
    ]
]:
    """Get Several Audiobooks

     Get Spotify catalog information for several audiobooks identified by their Spotify IDs. Audiobooks
    are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.
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
        Response[Union[GetMultipleAudiobooksResponse200, GetMultipleAudiobooksResponse401, GetMultipleAudiobooksResponse403, GetMultipleAudiobooksResponse429]]
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
        GetMultipleAudiobooksResponse200,
        GetMultipleAudiobooksResponse401,
        GetMultipleAudiobooksResponse403,
        GetMultipleAudiobooksResponse429,
    ]
]:
    """Get Several Audiobooks

     Get Spotify catalog information for several audiobooks identified by their Spotify IDs. Audiobooks
    are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.
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
        Union[GetMultipleAudiobooksResponse200, GetMultipleAudiobooksResponse401, GetMultipleAudiobooksResponse403, GetMultipleAudiobooksResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            market=market,
        )
    ).parsed
