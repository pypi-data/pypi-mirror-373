from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.audio_analysis_object import AudioAnalysisObject
from ...models.get_audio_analysis_response_401 import GetAudioAnalysisResponse401
from ...models.get_audio_analysis_response_403 import GetAudioAnalysisResponse403
from ...models.get_audio_analysis_response_429 import GetAudioAnalysisResponse429
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/audio-analysis/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
]:
    if response.status_code == 200:
        response_200 = AudioAnalysisObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetAudioAnalysisResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetAudioAnalysisResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetAudioAnalysisResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
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
    Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
]:
    """Get Track's Audio Analysis

     Get a low-level audio analysis for a track in the Spotify catalog. The audio analysis describes the
    track’s structure and musical content, including rhythm, pitch, and timbre.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]]
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
    Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
]:
    """Get Track's Audio Analysis

     Get a low-level audio analysis for a track in the Spotify catalog. The audio analysis describes the
    track’s structure and musical content, including rhythm, pitch, and timbre.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
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
    Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
]:
    """Get Track's Audio Analysis

     Get a low-level audio analysis for a track in the Spotify catalog. The audio analysis describes the
    track’s structure and musical content, including rhythm, pitch, and timbre.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]]
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
    Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
]:
    """Get Track's Audio Analysis

     Get a low-level audio analysis for a track in the Spotify catalog. The audio analysis describes the
    track’s structure and musical content, including rhythm, pitch, and timbre.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids)
            for the track.
             Example: 11dFghVXANMlKmJXsNCbNl.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AudioAnalysisObject, GetAudioAnalysisResponse401, GetAudioAnalysisResponse403, GetAudioAnalysisResponse429]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
