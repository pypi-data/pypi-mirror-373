from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FollowersObject")


@_attrs_define
class FollowersObject:
    """
    Attributes:
        href (Union[None, Unset, str]): This will always be set to null, as the Web API does not support it at the
            moment.
        total (Union[Unset, int]): The total number of followers.
    """

    href: Union[None, Unset, str] = UNSET
    total: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        href: Union[None, Unset, str]
        if isinstance(self.href, Unset):
            href = UNSET
        else:
            href = self.href

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if href is not UNSET:
            field_dict["href"] = href
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_href(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        href = _parse_href(d.pop("href", UNSET))

        total = d.pop("total", UNSET)

        followers_object = cls(
            href=href,
            total=total,
        )

        followers_object.additional_properties = d
        return followers_object

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
