from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PagingObject")


@_attrs_define
class PagingObject:
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
    """

    href: str
    limit: int
    next_: Union[None, str]
    offset: int
    previous: Union[None, str]
    total: int
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        paging_object = cls(
            href=href,
            limit=limit,
            next_=next_,
            offset=offset,
            previous=previous,
            total=total,
        )

        paging_object.additional_properties = d
        return paging_object

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
