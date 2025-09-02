from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cursor_object import CursorObject


T = TypeVar("T", bound="CursorPagingObject")


@_attrs_define
class CursorPagingObject:
    """
    Attributes:
        cursors (Union[Unset, CursorObject]):
        href (Union[Unset, str]): A link to the Web API endpoint returning the full result of the request.
        limit (Union[Unset, int]): The maximum number of items in the response (as set in the query or by default).
        next_ (Union[Unset, str]): URL to the next page of items. ( `null` if none)
        total (Union[Unset, int]): The total number of items available to return.
    """

    cursors: Union[Unset, "CursorObject"] = UNSET
    href: Union[Unset, str] = UNSET
    limit: Union[Unset, int] = UNSET
    next_: Union[Unset, str] = UNSET
    total: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cursors: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.cursors, Unset):
            cursors = self.cursors.to_dict()

        href = self.href

        limit = self.limit

        next_ = self.next_

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cursors is not UNSET:
            field_dict["cursors"] = cursors
        if href is not UNSET:
            field_dict["href"] = href
        if limit is not UNSET:
            field_dict["limit"] = limit
        if next_ is not UNSET:
            field_dict["next"] = next_
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cursor_object import CursorObject

        d = dict(src_dict)
        _cursors = d.pop("cursors", UNSET)
        cursors: Union[Unset, CursorObject]
        if isinstance(_cursors, Unset):
            cursors = UNSET
        else:
            cursors = CursorObject.from_dict(_cursors)

        href = d.pop("href", UNSET)

        limit = d.pop("limit", UNSET)

        next_ = d.pop("next", UNSET)

        total = d.pop("total", UNSET)

        cursor_paging_object = cls(
            cursors=cursors,
            href=href,
            limit=limit,
            next_=next_,
            total=total,
        )

        cursor_paging_object.additional_properties = d
        return cursor_paging_object

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
