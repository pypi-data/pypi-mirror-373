from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.transfer_a_users_playback_body import TransferAUsersPlaybackBody
from ...models.transfer_a_users_playback_response_401 import TransferAUsersPlaybackResponse401
from ...models.transfer_a_users_playback_response_403 import TransferAUsersPlaybackResponse403
from ...models.transfer_a_users_playback_response_429 import TransferAUsersPlaybackResponse429
from ...types import Response


def _get_kwargs(
    *,
    body: TransferAUsersPlaybackBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/player",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 401:
        response_401 = TransferAUsersPlaybackResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = TransferAUsersPlaybackResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = TransferAUsersPlaybackResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
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
    body: TransferAUsersPlaybackBody,
) -> Response[
    Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
]:
    """Transfer Playback

     Transfer playback to a new device and optionally begin playback. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        body (TransferAUsersPlaybackBody):  Example: {'device_ids': ['74ASZWbe4lXaubB36ztrGX']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]]
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
    body: TransferAUsersPlaybackBody,
) -> Optional[
    Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
]:
    """Transfer Playback

     Transfer playback to a new device and optionally begin playback. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        body (TransferAUsersPlaybackBody):  Example: {'device_ids': ['74ASZWbe4lXaubB36ztrGX']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: TransferAUsersPlaybackBody,
) -> Response[
    Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
]:
    """Transfer Playback

     Transfer playback to a new device and optionally begin playback. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        body (TransferAUsersPlaybackBody):  Example: {'device_ids': ['74ASZWbe4lXaubB36ztrGX']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: TransferAUsersPlaybackBody,
) -> Optional[
    Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
]:
    """Transfer Playback

     Transfer playback to a new device and optionally begin playback. This API only works for users who
    have Spotify Premium. The order of execution is not guaranteed when you use this API with other
    Player API endpoints.

    Args:
        body (TransferAUsersPlaybackBody):  Example: {'device_ids': ['74ASZWbe4lXaubB36ztrGX']}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TransferAUsersPlaybackResponse401, TransferAUsersPlaybackResponse403, TransferAUsersPlaybackResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
