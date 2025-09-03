from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_several_audio_features_response_200 import GetSeveralAudioFeaturesResponse200
from ...models.get_several_audio_features_response_401 import GetSeveralAudioFeaturesResponse401
from ...models.get_several_audio_features_response_403 import GetSeveralAudioFeaturesResponse403
from ...models.get_several_audio_features_response_429 import GetSeveralAudioFeaturesResponse429
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
        "url": "/audio-features",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetSeveralAudioFeaturesResponse200,
        GetSeveralAudioFeaturesResponse401,
        GetSeveralAudioFeaturesResponse403,
        GetSeveralAudioFeaturesResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetSeveralAudioFeaturesResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetSeveralAudioFeaturesResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetSeveralAudioFeaturesResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetSeveralAudioFeaturesResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetSeveralAudioFeaturesResponse200,
        GetSeveralAudioFeaturesResponse401,
        GetSeveralAudioFeaturesResponse403,
        GetSeveralAudioFeaturesResponse429,
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
        GetSeveralAudioFeaturesResponse200,
        GetSeveralAudioFeaturesResponse401,
        GetSeveralAudioFeaturesResponse403,
        GetSeveralAudioFeaturesResponse429,
    ]
]:
    """Get Several Tracks' Audio Features

     Get audio features for multiple tracks based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids)
            for the tracks. Maximum: 100 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetSeveralAudioFeaturesResponse200, GetSeveralAudioFeaturesResponse401, GetSeveralAudioFeaturesResponse403, GetSeveralAudioFeaturesResponse429]]
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
        GetSeveralAudioFeaturesResponse200,
        GetSeveralAudioFeaturesResponse401,
        GetSeveralAudioFeaturesResponse403,
        GetSeveralAudioFeaturesResponse429,
    ]
]:
    """Get Several Tracks' Audio Features

     Get audio features for multiple tracks based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids)
            for the tracks. Maximum: 100 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetSeveralAudioFeaturesResponse200, GetSeveralAudioFeaturesResponse401, GetSeveralAudioFeaturesResponse403, GetSeveralAudioFeaturesResponse429]
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
        GetSeveralAudioFeaturesResponse200,
        GetSeveralAudioFeaturesResponse401,
        GetSeveralAudioFeaturesResponse403,
        GetSeveralAudioFeaturesResponse429,
    ]
]:
    """Get Several Tracks' Audio Features

     Get audio features for multiple tracks based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids)
            for the tracks. Maximum: 100 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetSeveralAudioFeaturesResponse200, GetSeveralAudioFeaturesResponse401, GetSeveralAudioFeaturesResponse403, GetSeveralAudioFeaturesResponse429]]
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
        GetSeveralAudioFeaturesResponse200,
        GetSeveralAudioFeaturesResponse401,
        GetSeveralAudioFeaturesResponse403,
        GetSeveralAudioFeaturesResponse429,
    ]
]:
    """Get Several Tracks' Audio Features

     Get audio features for multiple tracks based on their Spotify IDs.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids)
            for the tracks. Maximum: 100 IDs.
             Example: 7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetSeveralAudioFeaturesResponse200, GetSeveralAudioFeaturesResponse401, GetSeveralAudioFeaturesResponse403, GetSeveralAudioFeaturesResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
        )
    ).parsed
