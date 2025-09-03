from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.check_users_saved_audiobooks_response_401 import CheckUsersSavedAudiobooksResponse401
from ...models.check_users_saved_audiobooks_response_403 import CheckUsersSavedAudiobooksResponse403
from ...models.check_users_saved_audiobooks_response_429 import CheckUsersSavedAudiobooksResponse429
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
        "url": "/me/audiobooks/contains",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CheckUsersSavedAudiobooksResponse401,
        CheckUsersSavedAudiobooksResponse403,
        CheckUsersSavedAudiobooksResponse429,
        list[bool],
    ]
]:
    if response.status_code == 200:
        response_200 = cast(list[bool], response.json())

        return response_200

    if response.status_code == 401:
        response_401 = CheckUsersSavedAudiobooksResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = CheckUsersSavedAudiobooksResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = CheckUsersSavedAudiobooksResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CheckUsersSavedAudiobooksResponse401,
        CheckUsersSavedAudiobooksResponse403,
        CheckUsersSavedAudiobooksResponse429,
        list[bool],
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
        CheckUsersSavedAudiobooksResponse401,
        CheckUsersSavedAudiobooksResponse403,
        CheckUsersSavedAudiobooksResponse429,
        list[bool],
    ]
]:
    """Check User's Saved Audiobooks

     Check if one or more audiobooks are already saved in the current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckUsersSavedAudiobooksResponse401, CheckUsersSavedAudiobooksResponse403, CheckUsersSavedAudiobooksResponse429, list[bool]]]
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
        CheckUsersSavedAudiobooksResponse401,
        CheckUsersSavedAudiobooksResponse403,
        CheckUsersSavedAudiobooksResponse429,
        list[bool],
    ]
]:
    """Check User's Saved Audiobooks

     Check if one or more audiobooks are already saved in the current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckUsersSavedAudiobooksResponse401, CheckUsersSavedAudiobooksResponse403, CheckUsersSavedAudiobooksResponse429, list[bool]]
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
        CheckUsersSavedAudiobooksResponse401,
        CheckUsersSavedAudiobooksResponse403,
        CheckUsersSavedAudiobooksResponse429,
        list[bool],
    ]
]:
    """Check User's Saved Audiobooks

     Check if one or more audiobooks are already saved in the current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CheckUsersSavedAudiobooksResponse401, CheckUsersSavedAudiobooksResponse403, CheckUsersSavedAudiobooksResponse429, list[bool]]]
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
        CheckUsersSavedAudiobooksResponse401,
        CheckUsersSavedAudiobooksResponse403,
        CheckUsersSavedAudiobooksResponse429,
        list[bool],
    ]
]:
    """Check User's Saved Audiobooks

     Check if one or more audiobooks are already saved in the current Spotify user's library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example:
            `ids=18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ`. Maximum: 50 IDs.
             Example: 18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ,7iHfbu1YPACw6oZPAFJtqe.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CheckUsersSavedAudiobooksResponse401, CheckUsersSavedAudiobooksResponse403, CheckUsersSavedAudiobooksResponse429, list[bool]]
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
        )
    ).parsed
