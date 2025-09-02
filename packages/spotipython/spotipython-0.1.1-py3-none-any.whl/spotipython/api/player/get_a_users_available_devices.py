from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_a_users_available_devices_response_200 import GetAUsersAvailableDevicesResponse200
from ...models.get_a_users_available_devices_response_401 import GetAUsersAvailableDevicesResponse401
from ...models.get_a_users_available_devices_response_403 import GetAUsersAvailableDevicesResponse403
from ...models.get_a_users_available_devices_response_429 import GetAUsersAvailableDevicesResponse429
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/me/player/devices",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetAUsersAvailableDevicesResponse200,
        GetAUsersAvailableDevicesResponse401,
        GetAUsersAvailableDevicesResponse403,
        GetAUsersAvailableDevicesResponse429,
    ]
]:
    if response.status_code == 200:
        response_200 = GetAUsersAvailableDevicesResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetAUsersAvailableDevicesResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetAUsersAvailableDevicesResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetAUsersAvailableDevicesResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetAUsersAvailableDevicesResponse200,
        GetAUsersAvailableDevicesResponse401,
        GetAUsersAvailableDevicesResponse403,
        GetAUsersAvailableDevicesResponse429,
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
) -> Response[
    Union[
        GetAUsersAvailableDevicesResponse200,
        GetAUsersAvailableDevicesResponse401,
        GetAUsersAvailableDevicesResponse403,
        GetAUsersAvailableDevicesResponse429,
    ]
]:
    """Get Available Devices

     Get information about a user’s available Spotify Connect devices. Some device models are not
    supported and will not be listed in the API response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAUsersAvailableDevicesResponse200, GetAUsersAvailableDevicesResponse401, GetAUsersAvailableDevicesResponse403, GetAUsersAvailableDevicesResponse429]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        GetAUsersAvailableDevicesResponse200,
        GetAUsersAvailableDevicesResponse401,
        GetAUsersAvailableDevicesResponse403,
        GetAUsersAvailableDevicesResponse429,
    ]
]:
    """Get Available Devices

     Get information about a user’s available Spotify Connect devices. Some device models are not
    supported and will not be listed in the API response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAUsersAvailableDevicesResponse200, GetAUsersAvailableDevicesResponse401, GetAUsersAvailableDevicesResponse403, GetAUsersAvailableDevicesResponse429]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        GetAUsersAvailableDevicesResponse200,
        GetAUsersAvailableDevicesResponse401,
        GetAUsersAvailableDevicesResponse403,
        GetAUsersAvailableDevicesResponse429,
    ]
]:
    """Get Available Devices

     Get information about a user’s available Spotify Connect devices. Some device models are not
    supported and will not be listed in the API response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetAUsersAvailableDevicesResponse200, GetAUsersAvailableDevicesResponse401, GetAUsersAvailableDevicesResponse403, GetAUsersAvailableDevicesResponse429]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        GetAUsersAvailableDevicesResponse200,
        GetAUsersAvailableDevicesResponse401,
        GetAUsersAvailableDevicesResponse403,
        GetAUsersAvailableDevicesResponse429,
    ]
]:
    """Get Available Devices

     Get information about a user’s available Spotify Connect devices. Some device models are not
    supported and will not be listed in the API response.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetAUsersAvailableDevicesResponse200, GetAUsersAvailableDevicesResponse401, GetAUsersAvailableDevicesResponse403, GetAUsersAvailableDevicesResponse429]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
