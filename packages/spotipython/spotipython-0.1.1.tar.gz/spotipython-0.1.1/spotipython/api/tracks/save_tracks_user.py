from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.save_tracks_user_body import SaveTracksUserBody
from ...models.save_tracks_user_response_401 import SaveTracksUserResponse401
from ...models.save_tracks_user_response_403 import SaveTracksUserResponse403
from ...models.save_tracks_user_response_429 import SaveTracksUserResponse429
from ...types import Response


def _get_kwargs(
    *,
    body: SaveTracksUserBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/tracks",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = SaveTracksUserResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SaveTracksUserResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SaveTracksUserResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SaveTracksUserBody,
) -> Response[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]:
    """Save Tracks for Current User

     Save one or more tracks to the current user's 'Your Music' library.

    Args:
        body (SaveTracksUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: SaveTracksUserBody,
) -> Optional[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]:
    """Save Tracks for Current User

     Save one or more tracks to the current user's 'Your Music' library.

    Args:
        body (SaveTracksUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SaveTracksUserBody,
) -> Response[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]:
    """Save Tracks for Current User

     Save one or more tracks to the current user's 'Your Music' library.

    Args:
        body (SaveTracksUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SaveTracksUserBody,
) -> Optional[Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]]:
    """Save Tracks for Current User

     Save one or more tracks to the current user's 'Your Music' library.

    Args:
        body (SaveTracksUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveTracksUserResponse401, SaveTracksUserResponse403, SaveTracksUserResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
