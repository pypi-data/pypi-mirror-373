from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_an_artists_related_artists_response_200 import GetAnArtistsRelatedArtistsResponse200
from ...models.get_an_artists_related_artists_response_401 import GetAnArtistsRelatedArtistsResponse401
from ...models.get_an_artists_related_artists_response_403 import GetAnArtistsRelatedArtistsResponse403
from ...models.get_an_artists_related_artists_response_429 import GetAnArtistsRelatedArtistsResponse429
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/artists/{id}/related-artists",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetAnArtistsRelatedArtistsResponse200,
        GetAnArtistsRelatedArtistsResponse401,
        GetAnArtistsRelatedArtistsResponse403,
        GetAnArtistsRelatedArtistsResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetAnArtistsRelatedArtistsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetAnArtistsRelatedArtistsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetAnArtistsRelatedArtistsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetAnArtistsRelatedArtistsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetAnArtistsRelatedArtistsResponse200,
        GetAnArtistsRelatedArtistsResponse401,
        GetAnArtistsRelatedArtistsResponse403,
        GetAnArtistsRelatedArtistsResponse429,
    ]
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
    Union[
        GetAnArtistsRelatedArtistsResponse200,
        GetAnArtistsRelatedArtistsResponse401,
        GetAnArtistsRelatedArtistsResponse403,
        GetAnArtistsRelatedArtistsResponse429,
    ]
]:
    """Get Artist's Related Artists

     Get Spotify catalog information about artists similar to a given artist. Similarity is based on
    analysis of the Spotify community's listening history.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAnArtistsRelatedArtistsResponse200, GetAnArtistsRelatedArtistsResponse401, GetAnArtistsRelatedArtistsResponse403, GetAnArtistsRelatedArtistsResponse429]]
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
    Union[
        GetAnArtistsRelatedArtistsResponse200,
        GetAnArtistsRelatedArtistsResponse401,
        GetAnArtistsRelatedArtistsResponse403,
        GetAnArtistsRelatedArtistsResponse429,
    ]
]:
    """Get Artist's Related Artists

     Get Spotify catalog information about artists similar to a given artist. Similarity is based on
    analysis of the Spotify community's listening history.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAnArtistsRelatedArtistsResponse200, GetAnArtistsRelatedArtistsResponse401, GetAnArtistsRelatedArtistsResponse403, GetAnArtistsRelatedArtistsResponse429]
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
    Union[
        GetAnArtistsRelatedArtistsResponse200,
        GetAnArtistsRelatedArtistsResponse401,
        GetAnArtistsRelatedArtistsResponse403,
        GetAnArtistsRelatedArtistsResponse429,
    ]
]:
    """Get Artist's Related Artists

     Get Spotify catalog information about artists similar to a given artist. Similarity is based on
    analysis of the Spotify community's listening history.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAnArtistsRelatedArtistsResponse200, GetAnArtistsRelatedArtistsResponse401, GetAnArtistsRelatedArtistsResponse403, GetAnArtistsRelatedArtistsResponse429]]
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
    Union[
        GetAnArtistsRelatedArtistsResponse200,
        GetAnArtistsRelatedArtistsResponse401,
        GetAnArtistsRelatedArtistsResponse403,
        GetAnArtistsRelatedArtistsResponse429,
    ]
]:
    """Get Artist's Related Artists

     Get Spotify catalog information about artists similar to a given artist. Similarity is based on
    analysis of the Spotify community's listening history.

    Args:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) of the
            artist.
             Example: 0TnOYISbd1XYRBk9myaseg.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAnArtistsRelatedArtistsResponse200, GetAnArtistsRelatedArtistsResponse401, GetAnArtistsRelatedArtistsResponse403, GetAnArtistsRelatedArtistsResponse429]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
