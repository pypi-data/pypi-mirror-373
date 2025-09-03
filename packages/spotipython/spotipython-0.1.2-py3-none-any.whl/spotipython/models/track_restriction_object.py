from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TrackRestrictionObject")


@_attrs_define
class TrackRestrictionObject:
    """
    Attributes:
        reason (Union[Unset, str]): The reason for the restriction. Supported values:
            - `market` - The content item is not available in the given market.
            - `product` - The content item is not available for the user's subscription type.
            - `explicit` - The content item is explicit and the user's account is set to not play explicit content.

            Additional reasons may be added in the future.
            **Note**: If you use this field, make sure that your application safely handles unknown values.
    """

    reason: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reason = d.pop("reason", UNSET)

        track_restriction_object = cls(
            reason=reason,
        )

        track_restriction_object.additional_properties = d
        return track_restriction_object

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
