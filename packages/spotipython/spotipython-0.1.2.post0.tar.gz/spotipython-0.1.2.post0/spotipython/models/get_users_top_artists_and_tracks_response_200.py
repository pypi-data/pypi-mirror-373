from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artist_object import ArtistObject
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="GetUsersTopArtistsAndTracksResponse200")


@_attrs_define
class GetUsersTopArtistsAndTracksResponse200:
    """
    Attributes:
        href (str): A link to the Web API endpoint returning the full result of the request
             Example: https://api.spotify.com/v1/me/shows?offset=0&limit=20
            .
        limit (int): The maximum number of items in the response (as set in the query or by default).
             Example: 20.
        next_ (Union[None, str]): URL to the next page of items. ( `null` if none)
             Example: https://api.spotify.com/v1/me/shows?offset=1&limit=1.
        offset (int): The offset of the items returned (as set in the query or by default)
        previous (Union[None, str]): URL to the previous page of items. ( `null` if none)
             Example: https://api.spotify.com/v1/me/shows?offset=1&limit=1.
        total (int): The total number of items available to return.
             Example: 4.
        items (Union[Unset, list[Union['ArtistObject', 'TrackObject']]]):
    """

    href: str
    limit: int
    next_: Union[None, str]
    offset: int
    previous: Union[None, str]
    total: int
    items: Union[Unset, list[Union["ArtistObject", "TrackObject"]]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.artist_object import ArtistObject

        href = self.href

        limit = self.limit

        next_: Union[None, str]
        next_ = self.next_

        offset = self.offset

        previous: Union[None, str]
        previous = self.previous

        total = self.total

        items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item: dict[str, Any]
                if isinstance(items_item_data, ArtistObject):
                    items_item = items_item_data.to_dict()
                else:
                    items_item = items_item_data.to_dict()

                items.append(items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "href": href,
                "limit": limit,
                "next": next_,
                "offset": offset,
                "previous": previous,
                "total": total,
            }
        )
        if items is not UNSET:
            field_dict["items"] = items

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artist_object import ArtistObject
        from ..models.track_object import TrackObject

        d = dict(src_dict)
        href = d.pop("href")

        limit = d.pop("limit")

        def _parse_next_(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        next_ = _parse_next_(d.pop("next"))

        offset = d.pop("offset")

        def _parse_previous(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        previous = _parse_previous(d.pop("previous"))

        total = d.pop("total")

        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in _items or []:

            def _parse_items_item(data: object) -> Union["ArtistObject", "TrackObject"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    items_item_type_0 = ArtistObject.from_dict(data)

                    return items_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                items_item_type_1 = TrackObject.from_dict(data)

                return items_item_type_1

            items_item = _parse_items_item(items_item_data)

            items.append(items_item)

        get_users_top_artists_and_tracks_response_200 = cls(
            href=href,
            limit=limit,
            next_=next_,
            offset=offset,
            previous=previous,
            total=total,
            items=items,
        )

        get_users_top_artists_and_tracks_response_200.additional_properties = d
        return get_users_top_artists_and_tracks_response_200

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
