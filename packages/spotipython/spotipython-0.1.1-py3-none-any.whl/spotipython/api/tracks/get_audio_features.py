from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.audio_features_object import AudioFeaturesObject
from ...models.get_audio_features_response_401 import GetAudioFeaturesResponse401
from ...models.get_audio_features_response_403 import GetAudioFeaturesResponse403
from ...models.get_audio_features_response_429 import GetAudioFeaturesResponse429
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/audio-features/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
]:
    if response.status_code == 200:
        response_200 = AudioFeaturesObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetAudioFeaturesResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetAudioFeaturesResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetAudioFeaturesResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
]:
    """Get Track's Audio Features

     Get audio feature information for a single track identified by its unique
    Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the
            track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
]:
    """Get Track's Audio Features

     Get audio feature information for a single track identified by its unique
    Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the
            track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
]:
    """Get Track's Audio Features

     Get audio feature information for a single track identified by its unique
    Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the
            track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
]:
    """Get Track's Audio Features

     Get audio feature information for a single track identified by its unique
    Spotify ID.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the
            track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AudioFeaturesObject, GetAudioFeaturesResponse401, GetAudioFeaturesResponse403, GetAudioFeaturesResponse429]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
