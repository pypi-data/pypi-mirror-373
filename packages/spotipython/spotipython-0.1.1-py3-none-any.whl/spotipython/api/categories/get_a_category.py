from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.category_object import CategoryObject
from ...models.get_a_category_response_401 import GetACategoryResponse401
from ...models.get_a_category_response_403 import GetACategoryResponse403
from ...models.get_a_category_response_429 import GetACategoryResponse429
from ...types import UNSET, Response, Unset


def _get_kwargs(
    category_id: str,
    *,
    locale: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["locale"] = locale

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/browse/categories/{category_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]:
    if response.status_code == 200:
        response_200 = CategoryObject.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = GetACategoryResponse401.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = GetACategoryResponse403.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = GetACategoryResponse429.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    category_id: str,
    *,
    client: AuthenticatedClient,
    locale: Union[Unset, str] = UNSET,
) -> Response[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]:
    """Get Single Browse Category

     Get a single category used to tag items in Spotify (on, for example, the Spotify player’s “Browse”
    tab).

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        locale=locale,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    category_id: str,
    *,
    client: AuthenticatedClient,
    locale: Union[Unset, str] = UNSET,
) -> Optional[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]:
    """Get Single Browse Category

     Get a single category used to tag items in Spotify (on, for example, the Spotify player’s “Browse”
    tab).

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]
    """

    return sync_detailed(
        category_id=category_id,
        client=client,
        locale=locale,
    ).parsed


async def asyncio_detailed(
    category_id: str,
    *,
    client: AuthenticatedClient,
    locale: Union[Unset, str] = UNSET,
) -> Response[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]:
    """Get Single Browse Category

     Get a single category used to tag items in Spotify (on, for example, the Spotify player’s “Browse”
    tab).

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        locale=locale,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    category_id: str,
    *,
    client: AuthenticatedClient,
    locale: Union[Unset, str] = UNSET,
) -> Optional[Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]]:
    """Get Single Browse Category

     Get a single category used to tag items in Spotify (on, for example, the Spotify player’s “Browse”
    tab).

    Args:
        category_id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-
            ids) for the category.
             Example: dinner.
        locale (Union[Unset, str]): The desired language, consisting of an [ISO
            639-1](http://en.wikipedia.org/wiki/ISO_639-1) language code and an [ISO 3166-1 alpha-2
            country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), joined by an underscore.
            For example: `es_MX`, meaning &quot;Spanish (Mexico)&quot;. Provide this parameter if you
            want the category strings returned in a particular language.<br/> _**Note**: if `locale`
            is not supplied, or if the specified language is not available, the category strings
            returned will be in the Spotify default language (American English)._
             Example: sv_SE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CategoryObject, GetACategoryResponse401, GetACategoryResponse403, GetACategoryResponse429]
    """

    return (
        await asyncio_detailed(
            category_id=category_id,
            client=client,
            locale=locale,
        )
    ).parsed
