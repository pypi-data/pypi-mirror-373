from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.saved_episode_object import SavedEpisodeObject


T = TypeVar("T", bound="PagingSavedEpisodeObject")


@_attrs_define
class PagingSavedEpisodeObject:
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
        items (Union[Unset, list['SavedEpisodeObject']]):
    """

    href: str
    limit: int
    next_: Union[None, str]
    offset: int
    previous: Union[None, str]
    total: int
    items: Union[Unset, list["SavedEpisodeObject"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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
        from ..models.saved_episode_object import SavedEpisodeObject

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
            items_item = SavedEpisodeObject.from_dict(items_item_data)

            items.append(items_item)

        paging_saved_episode_object = cls(
            href=href,
            limit=limit,
            next_=next_,
            offset=offset,
            previous=previous,
            total=total,
            items=items,
        )

        paging_saved_episode_object.additional_properties = d
        return paging_saved_episode_object

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
