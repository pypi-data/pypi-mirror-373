from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_recommendations_response_401 import GetRecommendationsResponse401
from ...models.get_recommendations_response_403 import GetRecommendationsResponse403
from ...models.get_recommendations_response_429 import GetRecommendationsResponse429
from ...models.recommendations_object import RecommendationsObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 20,
    market: Union[Unset, str] = UNSET,
    seed_artists: str,
    seed_genres: str,
    seed_tracks: str,
    min_acousticness: Union[Unset, float] = UNSET,
    max_acousticness: Union[Unset, float] = UNSET,
    target_acousticness: Union[Unset, float] = UNSET,
    min_danceability: Union[Unset, float] = UNSET,
    max_danceability: Union[Unset, float] = UNSET,
    target_danceability: Union[Unset, float] = UNSET,
    min_duration_ms: Union[Unset, int] = UNSET,
    max_duration_ms: Union[Unset, int] = UNSET,
    target_duration_ms: Union[Unset, int] = UNSET,
    min_energy: Union[Unset, float] = UNSET,
    max_energy: Union[Unset, float] = UNSET,
    target_energy: Union[Unset, float] = UNSET,
    min_instrumentalness: Union[Unset, float] = UNSET,
    max_instrumentalness: Union[Unset, float] = UNSET,
    target_instrumentalness: Union[Unset, float] = UNSET,
    min_key: Union[Unset, int] = UNSET,
    max_key: Union[Unset, int] = UNSET,
    target_key: Union[Unset, int] = UNSET,
    min_liveness: Union[Unset, float] = UNSET,
    max_liveness: Union[Unset, float] = UNSET,
    target_liveness: Union[Unset, float] = UNSET,
    min_loudness: Union[Unset, float] = UNSET,
    max_loudness: Union[Unset, float] = UNSET,
    target_loudness: Union[Unset, float] = UNSET,
    min_mode: Union[Unset, int] = UNSET,
    max_mode: Union[Unset, int] = UNSET,
    target_mode: Union[Unset, int] = UNSET,
    min_popularity: Union[Unset, int] = UNSET,
    max_popularity: Union[Unset, int] = UNSET,
    target_popularity: Union[Unset, int] = UNSET,
    min_speechiness: Union[Unset, float] = UNSET,
    max_speechiness: Union[Unset, float] = UNSET,
    target_speechiness: Union[Unset, float] = UNSET,
    min_tempo: Union[Unset, float] = UNSET,
    max_tempo: Union[Unset, float] = UNSET,
    target_tempo: Union[Unset, float] = UNSET,
    min_time_signature: Union[Unset, int] = UNSET,
    max_time_signature: Union[Unset, int] = UNSET,
    target_time_signature: Union[Unset, int] = UNSET,
    min_valence: Union[Unset, float] = UNSET,
    max_valence: Union[Unset, float] = UNSET,
    target_valence: Union[Unset, float] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["market"] = market

    params["seed_artists"] = seed_artists

    params["seed_genres"] = seed_genres

    params["seed_tracks"] = seed_tracks

    params["min_acousticness"] = min_acousticness

    params["max_acousticness"] = max_acousticness

    params["target_acousticness"] = target_acousticness

    params["min_danceability"] = min_danceability

    params["max_danceability"] = max_danceability

    params["target_danceability"] = target_danceability

    params["min_duration_ms"] = min_duration_ms

    params["max_duration_ms"] = max_duration_ms

    params["target_duration_ms"] = target_duration_ms

    params["min_energy"] = min_energy

    params["max_energy"] = max_energy

    params["target_energy"] = target_energy

    params["min_instrumentalness"] = min_instrumentalness

    params["max_instrumentalness"] = max_instrumentalness

    params["target_instrumentalness"] = target_instrumentalness

    params["min_key"] = min_key

    params["max_key"] = max_key

    params["target_key"] = target_key

    params["min_liveness"] = min_liveness

    params["max_liveness"] = max_liveness

    params["target_liveness"] = target_liveness

    params["min_loudness"] = min_loudness

    params["max_loudness"] = max_loudness

    params["target_loudness"] = target_loudness

    params["min_mode"] = min_mode

    params["max_mode"] = max_mode

    params["target_mode"] = target_mode

    params["min_popularity"] = min_popularity

    params["max_popularity"] = max_popularity

    params["target_popularity"] = target_popularity

    params["min_speechiness"] = min_speechiness

    params["max_speechiness"] = max_speechiness

    params["target_speechiness"] = target_speechiness

    params["min_tempo"] = min_tempo

    params["max_tempo"] = max_tempo

    params["target_tempo"] = target_tempo

    params["min_time_signature"] = min_time_signature

    params["max_time_signature"] = max_time_signature

    params["target_time_signature"] = target_time_signature

    params["min_valence"] = min_valence

    params["max_valence"] = max_valence

    params["target_valence"] = target_valence

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/recommendations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetRecommendationsResponse401,
        GetRecommendationsResponse403,
        GetRecommendationsResponse429,
        RecommendationsObject,
    ]
]:
    if response.status_code == 200:
        response_200 = RecommendationsObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetRecommendationsResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetRecommendationsResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetRecommendationsResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetRecommendationsResponse401,
        GetRecommendationsResponse403,
        GetRecommendationsResponse429,
        RecommendationsObject,
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
    limit: Union[Unset, int] = 20,
    market: Union[Unset, str] = UNSET,
    seed_artists: str,
    seed_genres: str,
    seed_tracks: str,
    min_acousticness: Union[Unset, float] = UNSET,
    max_acousticness: Union[Unset, float] = UNSET,
    target_acousticness: Union[Unset, float] = UNSET,
    min_danceability: Union[Unset, float] = UNSET,
    max_danceability: Union[Unset, float] = UNSET,
    target_danceability: Union[Unset, float] = UNSET,
    min_duration_ms: Union[Unset, int] = UNSET,
    max_duration_ms: Union[Unset, int] = UNSET,
    target_duration_ms: Union[Unset, int] = UNSET,
    min_energy: Union[Unset, float] = UNSET,
    max_energy: Union[Unset, float] = UNSET,
    target_energy: Union[Unset, float] = UNSET,
    min_instrumentalness: Union[Unset, float] = UNSET,
    max_instrumentalness: Union[Unset, float] = UNSET,
    target_instrumentalness: Union[Unset, float] = UNSET,
    min_key: Union[Unset, int] = UNSET,
    max_key: Union[Unset, int] = UNSET,
    target_key: Union[Unset, int] = UNSET,
    min_liveness: Union[Unset, float] = UNSET,
    max_liveness: Union[Unset, float] = UNSET,
    target_liveness: Union[Unset, float] = UNSET,
    min_loudness: Union[Unset, float] = UNSET,
    max_loudness: Union[Unset, float] = UNSET,
    target_loudness: Union[Unset, float] = UNSET,
    min_mode: Union[Unset, int] = UNSET,
    max_mode: Union[Unset, int] = UNSET,
    target_mode: Union[Unset, int] = UNSET,
    min_popularity: Union[Unset, int] = UNSET,
    max_popularity: Union[Unset, int] = UNSET,
    target_popularity: Union[Unset, int] = UNSET,
    min_speechiness: Union[Unset, float] = UNSET,
    max_speechiness: Union[Unset, float] = UNSET,
    target_speechiness: Union[Unset, float] = UNSET,
    min_tempo: Union[Unset, float] = UNSET,
    max_tempo: Union[Unset, float] = UNSET,
    target_tempo: Union[Unset, float] = UNSET,
    min_time_signature: Union[Unset, int] = UNSET,
    max_time_signature: Union[Unset, int] = UNSET,
    target_time_signature: Union[Unset, int] = UNSET,
    min_valence: Union[Unset, float] = UNSET,
    max_valence: Union[Unset, float] = UNSET,
    target_valence: Union[Unset, float] = UNSET,
) -> Response[
    Union[
        GetRecommendationsResponse401,
        GetRecommendationsResponse403,
        GetRecommendationsResponse429,
        RecommendationsObject,
    ]
]:
    r"""Get Recommendations

     Recommendations are generated based on the available information for a given seed entity and matched
    against similar artists and tracks. If there is sufficient information about the provided seeds, a
    list of tracks will be returned together with pool size details.

    For artists and tracks that are very new or obscure there might not be enough data to generate a
    list of tracks.

    Args:
        limit (Union[Unset, int]): The target size of the list of recommended tracks. For seeds
            with unusually small pools or when highly restrictive filtering is applied, it may be
            impossible to generate the requested number of recommended tracks. Debugging information
            for such cases is available in the response. Default: 20\. Minimum: 1\. Maximum: 100.
             Default: 20. Example: 10.
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
        seed_artists (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for seed artists.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_genres` and `seed_tracks` are not set_.
             Example: 4NHQUGzhtTLFvgF5SZesLK.
        seed_genres (str): A comma separated list of any genres in the set of [available genre
            seeds](/documentation/web-api/reference/get-recommendation-genres). Up to 5 seed values
            may be provided in any combination of `seed_artists`, `seed_tracks` and
            `seed_genres`.<br/> _**Note**: only required if `seed_artists` and `seed_tracks` are not
            set_.
             Example: classical,country.
        seed_tracks (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for a seed track.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_artists` and `seed_genres` are not set_.
             Example: 0c6xIDDpzE81m2q797ordA.
        min_acousticness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_acousticness (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_acousticness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_danceability (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_danceability (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_danceability (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_duration_ms (Union[Unset, int]): Target duration of the track (ms)
        min_energy (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_energy (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_energy (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard floor
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `min_tempo=140` would restrict
            results to only those tracks with a tempo of greater than 140 beats per minute.
        max_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard
            ceiling on the selected track attribute’s value can be provided. See tunable track
            attributes below for the list of available options. For example,
            `max_instrumentalness=0.35` would filter out most tracks that are likely to be
            instrumental.
        target_instrumentalness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_key (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_key (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_key (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_liveness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_liveness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_liveness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_loudness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_loudness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_loudness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_mode (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_mode (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_mode (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_popularity (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_popularity (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_popularity (Union[Unset, int]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_speechiness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_speechiness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_speechiness (Union[Unset, float]): For each of the tunable track attributes (below)
            a target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_tempo (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_tempo (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_tempo (Union[Unset, float]): Target tempo (BPM)
        min_time_signature (Union[Unset, int]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_time_signature (Union[Unset, int]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_time_signature (Union[Unset, int]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_valence (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_valence (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_valence (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetRecommendationsResponse401, GetRecommendationsResponse403, GetRecommendationsResponse429, RecommendationsObject]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        market=market,
        seed_artists=seed_artists,
        seed_genres=seed_genres,
        seed_tracks=seed_tracks,
        min_acousticness=min_acousticness,
        max_acousticness=max_acousticness,
        target_acousticness=target_acousticness,
        min_danceability=min_danceability,
        max_danceability=max_danceability,
        target_danceability=target_danceability,
        min_duration_ms=min_duration_ms,
        max_duration_ms=max_duration_ms,
        target_duration_ms=target_duration_ms,
        min_energy=min_energy,
        max_energy=max_energy,
        target_energy=target_energy,
        min_instrumentalness=min_instrumentalness,
        max_instrumentalness=max_instrumentalness,
        target_instrumentalness=target_instrumentalness,
        min_key=min_key,
        max_key=max_key,
        target_key=target_key,
        min_liveness=min_liveness,
        max_liveness=max_liveness,
        target_liveness=target_liveness,
        min_loudness=min_loudness,
        max_loudness=max_loudness,
        target_loudness=target_loudness,
        min_mode=min_mode,
        max_mode=max_mode,
        target_mode=target_mode,
        min_popularity=min_popularity,
        max_popularity=max_popularity,
        target_popularity=target_popularity,
        min_speechiness=min_speechiness,
        max_speechiness=max_speechiness,
        target_speechiness=target_speechiness,
        min_tempo=min_tempo,
        max_tempo=max_tempo,
        target_tempo=target_tempo,
        min_time_signature=min_time_signature,
        max_time_signature=max_time_signature,
        target_time_signature=target_time_signature,
        min_valence=min_valence,
        max_valence=max_valence,
        target_valence=target_valence,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    market: Union[Unset, str] = UNSET,
    seed_artists: str,
    seed_genres: str,
    seed_tracks: str,
    min_acousticness: Union[Unset, float] = UNSET,
    max_acousticness: Union[Unset, float] = UNSET,
    target_acousticness: Union[Unset, float] = UNSET,
    min_danceability: Union[Unset, float] = UNSET,
    max_danceability: Union[Unset, float] = UNSET,
    target_danceability: Union[Unset, float] = UNSET,
    min_duration_ms: Union[Unset, int] = UNSET,
    max_duration_ms: Union[Unset, int] = UNSET,
    target_duration_ms: Union[Unset, int] = UNSET,
    min_energy: Union[Unset, float] = UNSET,
    max_energy: Union[Unset, float] = UNSET,
    target_energy: Union[Unset, float] = UNSET,
    min_instrumentalness: Union[Unset, float] = UNSET,
    max_instrumentalness: Union[Unset, float] = UNSET,
    target_instrumentalness: Union[Unset, float] = UNSET,
    min_key: Union[Unset, int] = UNSET,
    max_key: Union[Unset, int] = UNSET,
    target_key: Union[Unset, int] = UNSET,
    min_liveness: Union[Unset, float] = UNSET,
    max_liveness: Union[Unset, float] = UNSET,
    target_liveness: Union[Unset, float] = UNSET,
    min_loudness: Union[Unset, float] = UNSET,
    max_loudness: Union[Unset, float] = UNSET,
    target_loudness: Union[Unset, float] = UNSET,
    min_mode: Union[Unset, int] = UNSET,
    max_mode: Union[Unset, int] = UNSET,
    target_mode: Union[Unset, int] = UNSET,
    min_popularity: Union[Unset, int] = UNSET,
    max_popularity: Union[Unset, int] = UNSET,
    target_popularity: Union[Unset, int] = UNSET,
    min_speechiness: Union[Unset, float] = UNSET,
    max_speechiness: Union[Unset, float] = UNSET,
    target_speechiness: Union[Unset, float] = UNSET,
    min_tempo: Union[Unset, float] = UNSET,
    max_tempo: Union[Unset, float] = UNSET,
    target_tempo: Union[Unset, float] = UNSET,
    min_time_signature: Union[Unset, int] = UNSET,
    max_time_signature: Union[Unset, int] = UNSET,
    target_time_signature: Union[Unset, int] = UNSET,
    min_valence: Union[Unset, float] = UNSET,
    max_valence: Union[Unset, float] = UNSET,
    target_valence: Union[Unset, float] = UNSET,
) -> Optional[
    Union[
        GetRecommendationsResponse401,
        GetRecommendationsResponse403,
        GetRecommendationsResponse429,
        RecommendationsObject,
    ]
]:
    r"""Get Recommendations

     Recommendations are generated based on the available information for a given seed entity and matched
    against similar artists and tracks. If there is sufficient information about the provided seeds, a
    list of tracks will be returned together with pool size details.

    For artists and tracks that are very new or obscure there might not be enough data to generate a
    list of tracks.

    Args:
        limit (Union[Unset, int]): The target size of the list of recommended tracks. For seeds
            with unusually small pools or when highly restrictive filtering is applied, it may be
            impossible to generate the requested number of recommended tracks. Debugging information
            for such cases is available in the response. Default: 20\. Minimum: 1\. Maximum: 100.
             Default: 20. Example: 10.
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
        seed_artists (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for seed artists.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_genres` and `seed_tracks` are not set_.
             Example: 4NHQUGzhtTLFvgF5SZesLK.
        seed_genres (str): A comma separated list of any genres in the set of [available genre
            seeds](/documentation/web-api/reference/get-recommendation-genres). Up to 5 seed values
            may be provided in any combination of `seed_artists`, `seed_tracks` and
            `seed_genres`.<br/> _**Note**: only required if `seed_artists` and `seed_tracks` are not
            set_.
             Example: classical,country.
        seed_tracks (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for a seed track.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_artists` and `seed_genres` are not set_.
             Example: 0c6xIDDpzE81m2q797ordA.
        min_acousticness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_acousticness (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_acousticness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_danceability (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_danceability (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_danceability (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_duration_ms (Union[Unset, int]): Target duration of the track (ms)
        min_energy (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_energy (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_energy (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard floor
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `min_tempo=140` would restrict
            results to only those tracks with a tempo of greater than 140 beats per minute.
        max_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard
            ceiling on the selected track attribute’s value can be provided. See tunable track
            attributes below for the list of available options. For example,
            `max_instrumentalness=0.35` would filter out most tracks that are likely to be
            instrumental.
        target_instrumentalness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_key (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_key (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_key (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_liveness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_liveness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_liveness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_loudness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_loudness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_loudness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_mode (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_mode (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_mode (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_popularity (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_popularity (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_popularity (Union[Unset, int]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_speechiness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_speechiness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_speechiness (Union[Unset, float]): For each of the tunable track attributes (below)
            a target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_tempo (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_tempo (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_tempo (Union[Unset, float]): Target tempo (BPM)
        min_time_signature (Union[Unset, int]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_time_signature (Union[Unset, int]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_time_signature (Union[Unset, int]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_valence (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_valence (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_valence (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetRecommendationsResponse401, GetRecommendationsResponse403, GetRecommendationsResponse429, RecommendationsObject]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        market=market,
        seed_artists=seed_artists,
        seed_genres=seed_genres,
        seed_tracks=seed_tracks,
        min_acousticness=min_acousticness,
        max_acousticness=max_acousticness,
        target_acousticness=target_acousticness,
        min_danceability=min_danceability,
        max_danceability=max_danceability,
        target_danceability=target_danceability,
        min_duration_ms=min_duration_ms,
        max_duration_ms=max_duration_ms,
        target_duration_ms=target_duration_ms,
        min_energy=min_energy,
        max_energy=max_energy,
        target_energy=target_energy,
        min_instrumentalness=min_instrumentalness,
        max_instrumentalness=max_instrumentalness,
        target_instrumentalness=target_instrumentalness,
        min_key=min_key,
        max_key=max_key,
        target_key=target_key,
        min_liveness=min_liveness,
        max_liveness=max_liveness,
        target_liveness=target_liveness,
        min_loudness=min_loudness,
        max_loudness=max_loudness,
        target_loudness=target_loudness,
        min_mode=min_mode,
        max_mode=max_mode,
        target_mode=target_mode,
        min_popularity=min_popularity,
        max_popularity=max_popularity,
        target_popularity=target_popularity,
        min_speechiness=min_speechiness,
        max_speechiness=max_speechiness,
        target_speechiness=target_speechiness,
        min_tempo=min_tempo,
        max_tempo=max_tempo,
        target_tempo=target_tempo,
        min_time_signature=min_time_signature,
        max_time_signature=max_time_signature,
        target_time_signature=target_time_signature,
        min_valence=min_valence,
        max_valence=max_valence,
        target_valence=target_valence,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    market: Union[Unset, str] = UNSET,
    seed_artists: str,
    seed_genres: str,
    seed_tracks: str,
    min_acousticness: Union[Unset, float] = UNSET,
    max_acousticness: Union[Unset, float] = UNSET,
    target_acousticness: Union[Unset, float] = UNSET,
    min_danceability: Union[Unset, float] = UNSET,
    max_danceability: Union[Unset, float] = UNSET,
    target_danceability: Union[Unset, float] = UNSET,
    min_duration_ms: Union[Unset, int] = UNSET,
    max_duration_ms: Union[Unset, int] = UNSET,
    target_duration_ms: Union[Unset, int] = UNSET,
    min_energy: Union[Unset, float] = UNSET,
    max_energy: Union[Unset, float] = UNSET,
    target_energy: Union[Unset, float] = UNSET,
    min_instrumentalness: Union[Unset, float] = UNSET,
    max_instrumentalness: Union[Unset, float] = UNSET,
    target_instrumentalness: Union[Unset, float] = UNSET,
    min_key: Union[Unset, int] = UNSET,
    max_key: Union[Unset, int] = UNSET,
    target_key: Union[Unset, int] = UNSET,
    min_liveness: Union[Unset, float] = UNSET,
    max_liveness: Union[Unset, float] = UNSET,
    target_liveness: Union[Unset, float] = UNSET,
    min_loudness: Union[Unset, float] = UNSET,
    max_loudness: Union[Unset, float] = UNSET,
    target_loudness: Union[Unset, float] = UNSET,
    min_mode: Union[Unset, int] = UNSET,
    max_mode: Union[Unset, int] = UNSET,
    target_mode: Union[Unset, int] = UNSET,
    min_popularity: Union[Unset, int] = UNSET,
    max_popularity: Union[Unset, int] = UNSET,
    target_popularity: Union[Unset, int] = UNSET,
    min_speechiness: Union[Unset, float] = UNSET,
    max_speechiness: Union[Unset, float] = UNSET,
    target_speechiness: Union[Unset, float] = UNSET,
    min_tempo: Union[Unset, float] = UNSET,
    max_tempo: Union[Unset, float] = UNSET,
    target_tempo: Union[Unset, float] = UNSET,
    min_time_signature: Union[Unset, int] = UNSET,
    max_time_signature: Union[Unset, int] = UNSET,
    target_time_signature: Union[Unset, int] = UNSET,
    min_valence: Union[Unset, float] = UNSET,
    max_valence: Union[Unset, float] = UNSET,
    target_valence: Union[Unset, float] = UNSET,
) -> Response[
    Union[
        GetRecommendationsResponse401,
        GetRecommendationsResponse403,
        GetRecommendationsResponse429,
        RecommendationsObject,
    ]
]:
    r"""Get Recommendations

     Recommendations are generated based on the available information for a given seed entity and matched
    against similar artists and tracks. If there is sufficient information about the provided seeds, a
    list of tracks will be returned together with pool size details.

    For artists and tracks that are very new or obscure there might not be enough data to generate a
    list of tracks.

    Args:
        limit (Union[Unset, int]): The target size of the list of recommended tracks. For seeds
            with unusually small pools or when highly restrictive filtering is applied, it may be
            impossible to generate the requested number of recommended tracks. Debugging information
            for such cases is available in the response. Default: 20\. Minimum: 1\. Maximum: 100.
             Default: 20. Example: 10.
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
        seed_artists (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for seed artists.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_genres` and `seed_tracks` are not set_.
             Example: 4NHQUGzhtTLFvgF5SZesLK.
        seed_genres (str): A comma separated list of any genres in the set of [available genre
            seeds](/documentation/web-api/reference/get-recommendation-genres). Up to 5 seed values
            may be provided in any combination of `seed_artists`, `seed_tracks` and
            `seed_genres`.<br/> _**Note**: only required if `seed_artists` and `seed_tracks` are not
            set_.
             Example: classical,country.
        seed_tracks (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for a seed track.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_artists` and `seed_genres` are not set_.
             Example: 0c6xIDDpzE81m2q797ordA.
        min_acousticness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_acousticness (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_acousticness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_danceability (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_danceability (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_danceability (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_duration_ms (Union[Unset, int]): Target duration of the track (ms)
        min_energy (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_energy (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_energy (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard floor
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `min_tempo=140` would restrict
            results to only those tracks with a tempo of greater than 140 beats per minute.
        max_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard
            ceiling on the selected track attribute’s value can be provided. See tunable track
            attributes below for the list of available options. For example,
            `max_instrumentalness=0.35` would filter out most tracks that are likely to be
            instrumental.
        target_instrumentalness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_key (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_key (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_key (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_liveness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_liveness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_liveness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_loudness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_loudness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_loudness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_mode (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_mode (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_mode (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_popularity (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_popularity (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_popularity (Union[Unset, int]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_speechiness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_speechiness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_speechiness (Union[Unset, float]): For each of the tunable track attributes (below)
            a target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_tempo (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_tempo (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_tempo (Union[Unset, float]): Target tempo (BPM)
        min_time_signature (Union[Unset, int]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_time_signature (Union[Unset, int]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_time_signature (Union[Unset, int]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_valence (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_valence (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_valence (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetRecommendationsResponse401, GetRecommendationsResponse403, GetRecommendationsResponse429, RecommendationsObject]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        market=market,
        seed_artists=seed_artists,
        seed_genres=seed_genres,
        seed_tracks=seed_tracks,
        min_acousticness=min_acousticness,
        max_acousticness=max_acousticness,
        target_acousticness=target_acousticness,
        min_danceability=min_danceability,
        max_danceability=max_danceability,
        target_danceability=target_danceability,
        min_duration_ms=min_duration_ms,
        max_duration_ms=max_duration_ms,
        target_duration_ms=target_duration_ms,
        min_energy=min_energy,
        max_energy=max_energy,
        target_energy=target_energy,
        min_instrumentalness=min_instrumentalness,
        max_instrumentalness=max_instrumentalness,
        target_instrumentalness=target_instrumentalness,
        min_key=min_key,
        max_key=max_key,
        target_key=target_key,
        min_liveness=min_liveness,
        max_liveness=max_liveness,
        target_liveness=target_liveness,
        min_loudness=min_loudness,
        max_loudness=max_loudness,
        target_loudness=target_loudness,
        min_mode=min_mode,
        max_mode=max_mode,
        target_mode=target_mode,
        min_popularity=min_popularity,
        max_popularity=max_popularity,
        target_popularity=target_popularity,
        min_speechiness=min_speechiness,
        max_speechiness=max_speechiness,
        target_speechiness=target_speechiness,
        min_tempo=min_tempo,
        max_tempo=max_tempo,
        target_tempo=target_tempo,
        min_time_signature=min_time_signature,
        max_time_signature=max_time_signature,
        target_time_signature=target_time_signature,
        min_valence=min_valence,
        max_valence=max_valence,
        target_valence=target_valence,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, int] = 20,
    market: Union[Unset, str] = UNSET,
    seed_artists: str,
    seed_genres: str,
    seed_tracks: str,
    min_acousticness: Union[Unset, float] = UNSET,
    max_acousticness: Union[Unset, float] = UNSET,
    target_acousticness: Union[Unset, float] = UNSET,
    min_danceability: Union[Unset, float] = UNSET,
    max_danceability: Union[Unset, float] = UNSET,
    target_danceability: Union[Unset, float] = UNSET,
    min_duration_ms: Union[Unset, int] = UNSET,
    max_duration_ms: Union[Unset, int] = UNSET,
    target_duration_ms: Union[Unset, int] = UNSET,
    min_energy: Union[Unset, float] = UNSET,
    max_energy: Union[Unset, float] = UNSET,
    target_energy: Union[Unset, float] = UNSET,
    min_instrumentalness: Union[Unset, float] = UNSET,
    max_instrumentalness: Union[Unset, float] = UNSET,
    target_instrumentalness: Union[Unset, float] = UNSET,
    min_key: Union[Unset, int] = UNSET,
    max_key: Union[Unset, int] = UNSET,
    target_key: Union[Unset, int] = UNSET,
    min_liveness: Union[Unset, float] = UNSET,
    max_liveness: Union[Unset, float] = UNSET,
    target_liveness: Union[Unset, float] = UNSET,
    min_loudness: Union[Unset, float] = UNSET,
    max_loudness: Union[Unset, float] = UNSET,
    target_loudness: Union[Unset, float] = UNSET,
    min_mode: Union[Unset, int] = UNSET,
    max_mode: Union[Unset, int] = UNSET,
    target_mode: Union[Unset, int] = UNSET,
    min_popularity: Union[Unset, int] = UNSET,
    max_popularity: Union[Unset, int] = UNSET,
    target_popularity: Union[Unset, int] = UNSET,
    min_speechiness: Union[Unset, float] = UNSET,
    max_speechiness: Union[Unset, float] = UNSET,
    target_speechiness: Union[Unset, float] = UNSET,
    min_tempo: Union[Unset, float] = UNSET,
    max_tempo: Union[Unset, float] = UNSET,
    target_tempo: Union[Unset, float] = UNSET,
    min_time_signature: Union[Unset, int] = UNSET,
    max_time_signature: Union[Unset, int] = UNSET,
    target_time_signature: Union[Unset, int] = UNSET,
    min_valence: Union[Unset, float] = UNSET,
    max_valence: Union[Unset, float] = UNSET,
    target_valence: Union[Unset, float] = UNSET,
) -> Optional[
    Union[
        GetRecommendationsResponse401,
        GetRecommendationsResponse403,
        GetRecommendationsResponse429,
        RecommendationsObject,
    ]
]:
    r"""Get Recommendations

     Recommendations are generated based on the available information for a given seed entity and matched
    against similar artists and tracks. If there is sufficient information about the provided seeds, a
    list of tracks will be returned together with pool size details.

    For artists and tracks that are very new or obscure there might not be enough data to generate a
    list of tracks.

    Args:
        limit (Union[Unset, int]): The target size of the list of recommended tracks. For seeds
            with unusually small pools or when highly restrictive filtering is applied, it may be
            impossible to generate the requested number of recommended tracks. Debugging information
            for such cases is available in the response. Default: 20\. Minimum: 1\. Maximum: 100.
             Default: 20. Example: 10.
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
        seed_artists (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for seed artists.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_genres` and `seed_tracks` are not set_.
             Example: 4NHQUGzhtTLFvgF5SZesLK.
        seed_genres (str): A comma separated list of any genres in the set of [available genre
            seeds](/documentation/web-api/reference/get-recommendation-genres). Up to 5 seed values
            may be provided in any combination of `seed_artists`, `seed_tracks` and
            `seed_genres`.<br/> _**Note**: only required if `seed_artists` and `seed_tracks` are not
            set_.
             Example: classical,country.
        seed_tracks (str): A comma separated list of [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for a seed track.  Up to 5 seed values may be provided in
            any combination of `seed_artists`, `seed_tracks` and `seed_genres`.<br/> _**Note**: only
            required if `seed_artists` and `seed_genres` are not set_.
             Example: 0c6xIDDpzE81m2q797ordA.
        min_acousticness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_acousticness (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_acousticness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_danceability (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_danceability (Union[Unset, float]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_danceability (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_duration_ms (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_duration_ms (Union[Unset, int]): Target duration of the track (ms)
        min_energy (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_energy (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_energy (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard floor
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `min_tempo=140` would restrict
            results to only those tracks with a tempo of greater than 140 beats per minute.
        max_instrumentalness (Union[Unset, float]): For each tunable track attribute, a hard
            ceiling on the selected track attribute’s value can be provided. See tunable track
            attributes below for the list of available options. For example,
            `max_instrumentalness=0.35` would filter out most tracks that are likely to be
            instrumental.
        target_instrumentalness (Union[Unset, float]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_key (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_key (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_key (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_liveness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_liveness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_liveness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_loudness (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_loudness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_loudness (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_mode (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_mode (Union[Unset, int]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_mode (Union[Unset, int]): For each of the tunable track attributes (below) a target
            value may be provided. Tracks with the attribute values nearest to the target values will
            be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_popularity (Union[Unset, int]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_popularity (Union[Unset, int]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_popularity (Union[Unset, int]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_speechiness (Union[Unset, float]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_speechiness (Union[Unset, float]): For each tunable track attribute, a hard ceiling on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `max_instrumentalness=0.35` would filter
            out most tracks that are likely to be instrumental.
        target_speechiness (Union[Unset, float]): For each of the tunable track attributes (below)
            a target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_tempo (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_tempo (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_tempo (Union[Unset, float]): Target tempo (BPM)
        min_time_signature (Union[Unset, int]): For each tunable track attribute, a hard floor on
            the selected track attribute’s value can be provided. See tunable track attributes below
            for the list of available options. For example, `min_tempo=140` would restrict results to
            only those tracks with a tempo of greater than 140 beats per minute.
        max_time_signature (Union[Unset, int]): For each tunable track attribute, a hard ceiling
            on the selected track attribute’s value can be provided. See tunable track attributes
            below for the list of available options. For example, `max_instrumentalness=0.35` would
            filter out most tracks that are likely to be instrumental.
        target_time_signature (Union[Unset, int]): For each of the tunable track attributes
            (below) a target value may be provided. Tracks with the attribute values nearest to the
            target values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.
        min_valence (Union[Unset, float]): For each tunable track attribute, a hard floor on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `min_tempo=140` would restrict results to only
            those tracks with a tempo of greater than 140 beats per minute.
        max_valence (Union[Unset, float]): For each tunable track attribute, a hard ceiling on the
            selected track attribute’s value can be provided. See tunable track attributes below for
            the list of available options. For example, `max_instrumentalness=0.35` would filter out
            most tracks that are likely to be instrumental.
        target_valence (Union[Unset, float]): For each of the tunable track attributes (below) a
            target value may be provided. Tracks with the attribute values nearest to the target
            values will be preferred. For example, you might request `target_energy=0.6` and
            `target_danceability=0.8`. All target values will be weighed equally in ranking results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetRecommendationsResponse401, GetRecommendationsResponse403, GetRecommendationsResponse429, RecommendationsObject]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            market=market,
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            seed_tracks=seed_tracks,
            min_acousticness=min_acousticness,
            max_acousticness=max_acousticness,
            target_acousticness=target_acousticness,
            min_danceability=min_danceability,
            max_danceability=max_danceability,
            target_danceability=target_danceability,
            min_duration_ms=min_duration_ms,
            max_duration_ms=max_duration_ms,
            target_duration_ms=target_duration_ms,
            min_energy=min_energy,
            max_energy=max_energy,
            target_energy=target_energy,
            min_instrumentalness=min_instrumentalness,
            max_instrumentalness=max_instrumentalness,
            target_instrumentalness=target_instrumentalness,
            min_key=min_key,
            max_key=max_key,
            target_key=target_key,
            min_liveness=min_liveness,
            max_liveness=max_liveness,
            target_liveness=target_liveness,
            min_loudness=min_loudness,
            max_loudness=max_loudness,
            target_loudness=target_loudness,
            min_mode=min_mode,
            max_mode=max_mode,
            target_mode=target_mode,
            min_popularity=min_popularity,
            max_popularity=max_popularity,
            target_popularity=target_popularity,
            min_speechiness=min_speechiness,
            max_speechiness=max_speechiness,
            target_speechiness=target_speechiness,
            min_tempo=min_tempo,
            max_tempo=max_tempo,
            target_tempo=target_tempo,
            min_time_signature=min_time_signature,
            max_time_signature=max_time_signature,
            target_time_signature=target_time_signature,
            min_valence=min_valence,
            max_valence=max_valence,
            target_valence=target_valence,
        )
    ).parsed
