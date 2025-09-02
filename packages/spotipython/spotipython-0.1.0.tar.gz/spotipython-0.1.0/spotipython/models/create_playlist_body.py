from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreatePlaylistBody")


@_attrs_define
class CreatePlaylistBody:
    """
    Example:
        {'description': 'New playlist description', 'name': 'New Playlist', 'public': False}

    Attributes:
        name (str): The name for the new playlist, for example `"Your Coolest Playlist"`. This name does not need to be
            unique; a user may have several playlists with the same name.
        collaborative (Union[Unset, bool]): Defaults to `false`. If `true` the playlist will be collaborative.
            _**Note**: to create a collaborative playlist you must also set `public` to `false`. To create collaborative
            playlists you must have granted `playlist-modify-private` and `playlist-modify-public`
            [scopes](/documentation/web-api/concepts/scopes/#list-of-scopes)._
        description (Union[Unset, str]): value for playlist description as displayed in Spotify Clients and in the Web
            API.
        public (Union[Unset, bool]): Defaults to `true`. If `true` the playlist will be public, if `false` it will be
            private. To be able to create private playlists, the user must have granted the `playlist-modify-private`
            [scope](/documentation/web-api/concepts/scopes/#list-of-scopes)
    """

    name: str
    collaborative: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    public: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        collaborative = self.collaborative

        description = self.description

        public = self.public

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if collaborative is not UNSET:
            field_dict["collaborative"] = collaborative
        if description is not UNSET:
            field_dict["description"] = description
        if public is not UNSET:
            field_dict["public"] = public

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        collaborative = d.pop("collaborative", UNSET)

        description = d.pop("description", UNSET)

        public = d.pop("public", UNSET)

        create_playlist_body = cls(
            name=name,
            collaborative=collaborative,
            description=description,
            public=public,
        )

        create_playlist_body.additional_properties = d
        return create_playlist_body

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
