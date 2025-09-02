from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangePlaylistDetailsBody")


@_attrs_define
class ChangePlaylistDetailsBody:
    """
    Example:
        {'description': 'Updated playlist description', 'name': 'Updated Playlist Name', 'public': False}

    Attributes:
        collaborative (Union[Unset, bool]): If `true`, the playlist will become collaborative and other users will be
            able to modify the playlist in their Spotify client. <br/>
            _**Note**: You can only set `collaborative` to `true` on non-public playlists._
        description (Union[Unset, str]): Value for playlist description as displayed in Spotify Clients and in the Web
            API.
        name (Union[Unset, str]): The new name for the playlist, for example `"My New Playlist Title"`
        public (Union[Unset, bool]): If `true` the playlist will be public, if `false` it will be private.
    """

    collaborative: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    public: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collaborative = self.collaborative

        description = self.description

        name = self.name

        public = self.public

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if collaborative is not UNSET:
            field_dict["collaborative"] = collaborative
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if public is not UNSET:
            field_dict["public"] = public

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        collaborative = d.pop("collaborative", UNSET)

        description = d.pop("description", UNSET)

        name = d.pop("name", UNSET)

        public = d.pop("public", UNSET)

        change_playlist_details_body = cls(
            collaborative=collaborative,
            description=description,
            name=name,
            public=public,
        )

        change_playlist_details_body.additional_properties = d
        return change_playlist_details_body

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
