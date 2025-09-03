from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExplicitContentSettingsObject")


@_attrs_define
class ExplicitContentSettingsObject:
    """
    Attributes:
        filter_enabled (Union[Unset, bool]): When `true`, indicates that explicit content should not be played.
        filter_locked (Union[Unset, bool]): When `true`, indicates that the explicit content setting is locked and can't
            be changed by the user.
    """

    filter_enabled: Union[Unset, bool] = UNSET
    filter_locked: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filter_enabled = self.filter_enabled

        filter_locked = self.filter_locked

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filter_enabled is not UNSET:
            field_dict["filter_enabled"] = filter_enabled
        if filter_locked is not UNSET:
            field_dict["filter_locked"] = filter_locked

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filter_enabled = d.pop("filter_enabled", UNSET)

        filter_locked = d.pop("filter_locked", UNSET)

        explicit_content_settings_object = cls(
            filter_enabled=filter_enabled,
            filter_locked=filter_locked,
        )

        explicit_content_settings_object.additional_properties = d
        return explicit_content_settings_object

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
