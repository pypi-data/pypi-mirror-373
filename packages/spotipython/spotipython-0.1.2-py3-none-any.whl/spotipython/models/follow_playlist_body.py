from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FollowPlaylistBody")


@_attrs_define
class FollowPlaylistBody:
    """
    Example:
        {'public': False}

    Attributes:
        public (Union[Unset, bool]): Defaults to `true`. If `true` the playlist will be included in user's public
            playlists (added to profile), if `false` it will remain private. For more about public/private status, see
            [Working with Playlists](/documentation/web-api/concepts/playlists)
    """

    public: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        public = self.public

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if public is not UNSET:
            field_dict["public"] = public

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        public = d.pop("public", UNSET)

        follow_playlist_body = cls(
            public=public,
        )

        follow_playlist_body.additional_properties = d
        return follow_playlist_body

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
