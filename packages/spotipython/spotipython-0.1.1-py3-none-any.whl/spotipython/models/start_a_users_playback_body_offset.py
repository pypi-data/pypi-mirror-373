from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="StartAUsersPlaybackBodyOffset")


@_attrs_define
class StartAUsersPlaybackBodyOffset:
    """Optional. Indicates from where in the context playback should start. Only available when context_uri corresponds to
    an album or playlist object
    "position" is zero based and can’t be negative. Example: `"offset": {"position": 5}`
    "uri" is a string representing the uri of the item to start at. Example: `"offset": {"uri":
    "spotify:track:1301WleyT98MSxVHPZCA6M"}`

    """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_a_users_playback_body_offset = cls()

        start_a_users_playback_body_offset.additional_properties = d
        return start_a_users_playback_body_offset

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
