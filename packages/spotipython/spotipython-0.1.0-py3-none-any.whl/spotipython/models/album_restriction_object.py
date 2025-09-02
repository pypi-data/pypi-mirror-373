from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.album_restriction_object_reason import AlbumRestrictionObjectReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="AlbumRestrictionObject")


@_attrs_define
class AlbumRestrictionObject:
    """
    Attributes:
        reason (Union[Unset, AlbumRestrictionObjectReason]): The reason for the restriction. Albums may be restricted if
            the content is not available in a given market, to the user's subscription type, or when the user's account is
            set to not play explicit content.
            Additional reasons may be added in the future.
    """

    reason: Union[Unset, AlbumRestrictionObjectReason] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason: Union[Unset, str] = UNSET
        if not isinstance(self.reason, Unset):
            reason = self.reason.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _reason = d.pop("reason", UNSET)
        reason: Union[Unset, AlbumRestrictionObjectReason]
        if isinstance(_reason, Unset):
            reason = UNSET
        else:
            reason = AlbumRestrictionObjectReason(_reason)

        album_restriction_object = cls(
            reason=reason,
        )

        album_restriction_object.additional_properties = d
        return album_restriction_object

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
