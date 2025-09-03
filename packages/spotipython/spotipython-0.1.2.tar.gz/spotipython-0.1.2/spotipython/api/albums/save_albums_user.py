from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.save_albums_user_body import SaveAlbumsUserBody
from ...models.save_albums_user_response_401 import SaveAlbumsUserResponse401
from ...models.save_albums_user_response_403 import SaveAlbumsUserResponse403
from ...models.save_albums_user_response_429 import SaveAlbumsUserResponse429
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: SaveAlbumsUserBody,
    ids: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["ids"] = ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/me/albums",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = SaveAlbumsUserResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = SaveAlbumsUserResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = SaveAlbumsUserResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: SaveAlbumsUserBody,
    ids: str,
) -> Response[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]:
    """Save Albums for Current User

     Save one or more albums to the current user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
        body (SaveAlbumsUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
        ids=ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: SaveAlbumsUserBody,
    ids: str,
) -> Optional[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]:
    """Save Albums for Current User

     Save one or more albums to the current user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
        body (SaveAlbumsUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]
    """

    return sync_detailed(
        client=client,
        body=body,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SaveAlbumsUserBody,
    ids: str,
) -> Response[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]:
    """Save Albums for Current User

     Save one or more albums to the current user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
        body (SaveAlbumsUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]
    """

    kwargs = _get_kwargs(
        body=body,
        ids=ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SaveAlbumsUserBody,
    ids: str,
) -> Optional[Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]]:
    """Save Albums for Current User

     Save one or more albums to the current user's 'Your Music' library.

    Args:
        ids (str): A comma-separated list of the [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids) for the albums. Maximum: 20 IDs.
             Example: 382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc.
        body (SaveAlbumsUserBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, SaveAlbumsUserResponse401, SaveAlbumsUserResponse403, SaveAlbumsUserResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            ids=ids,
        )
    ).parsed
