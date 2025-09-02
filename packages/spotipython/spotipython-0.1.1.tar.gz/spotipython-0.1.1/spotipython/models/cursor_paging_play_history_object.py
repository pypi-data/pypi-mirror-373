from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cursor_object import CursorObject
    from ..models.play_history_object import PlayHistoryObject


T = TypeVar("T", bound="CursorPagingPlayHistoryObject")


@_attrs_define
class CursorPagingPlayHistoryObject:
    """
    Attributes:
        href (Union[Unset, str]): A link to the Web API endpoint returning the full result of the request.
        limit (Union[Unset, int]): The maximum number of items in the response (as set in the query or by default).
        next_ (Union[Unset, str]): URL to the next page of items. ( `null` if none)
        cursors (Union[Unset, CursorObject]):
        total (Union[Unset, int]): The total number of items available to return.
        items (Union[Unset, list['PlayHistoryObject']]):
    """

    href: Union[Unset, str] = UNSET
    limit: Union[Unset, int] = UNSET
    next_: Union[Unset, str] = UNSET
    cursors: Union[Unset, "CursorObject"] = UNSET
    total: Union[Unset, int] = UNSET
    items: Union[Unset, list["PlayHistoryObject"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        href = self.href

        limit = self.limit

        next_ = self.next_

        cursors: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.cursors, Unset):
            cursors = self.cursors.to_dict()

        total = self.total

        items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if href is not UNSET:
            field_dict["href"] = href
        if limit is not UNSET:
            field_dict["limit"] = limit
        if next_ is not UNSET:
            field_dict["next"] = next_
        if cursors is not UNSET:
            field_dict["cursors"] = cursors
        if total is not UNSET:
            field_dict["total"] = total
        if items is not UNSET:
            field_dict["items"] = items

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cursor_object import CursorObject
        from ..models.play_history_object import PlayHistoryObject

        d = dict(src_dict)
        href = d.pop("href", UNSET)

        limit = d.pop("limit", UNSET)

        next_ = d.pop("next", UNSET)

        _cursors = d.pop("cursors", UNSET)
        cursors: Union[Unset, CursorObject]
        if isinstance(_cursors, Unset):
            cursors = UNSET
        else:
            cursors = CursorObject.from_dict(_cursors)

        total = d.pop("total", UNSET)

        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in _items or []:
            items_item = PlayHistoryObject.from_dict(items_item_data)

            items.append(items_item)

        cursor_paging_play_history_object = cls(
            href=href,
            limit=limit,
            next_=next_,
            cursors=cursors,
            total=total,
            items=items,
        )

        cursor_paging_play_history_object.additional_properties = d
        return cursor_paging_play_history_object

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
