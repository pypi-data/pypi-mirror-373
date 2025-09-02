from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.start_a_users_playback_body_offset import StartAUsersPlaybackBodyOffset


T = TypeVar("T", bound="StartAUsersPlaybackBody")


@_attrs_define
class StartAUsersPlaybackBody:
    """
    Example:
        {'context_uri': 'spotify:album:5ht7ItJgpBH7W6vJ5BqpPr', 'offset': {'position': 5}, 'position_ms': 0}

    Attributes:
        context_uri (Union[Unset, str]): Optional. Spotify URI of the context to play.
            Valid contexts are albums, artists & playlists.
            `{context_uri:"spotify:album:1Je1IMUlBXcx1Fz0WE7oPT"}`
        uris (Union[Unset, list[str]]): Optional. A JSON array of the Spotify track URIs to play.
            For example: `{"uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh", "spotify:track:1301WleyT98MSxVHPZCA6M"]}`
        offset (Union[Unset, StartAUsersPlaybackBodyOffset]): Optional. Indicates from where in the context playback
            should start. Only available when context_uri corresponds to an album or playlist object
            "position" is zero based and can’t be negative. Example: `"offset": {"position": 5}`
            "uri" is a string representing the uri of the item to start at. Example: `"offset": {"uri":
            "spotify:track:1301WleyT98MSxVHPZCA6M"}`
        position_ms (Union[Unset, int]): integer
    """

    context_uri: Union[Unset, str] = UNSET
    uris: Union[Unset, list[str]] = UNSET
    offset: Union[Unset, "StartAUsersPlaybackBodyOffset"] = UNSET
    position_ms: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        context_uri = self.context_uri

        uris: Union[Unset, list[str]] = UNSET
        if not isinstance(self.uris, Unset):
            uris = self.uris

        offset: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.offset, Unset):
            offset = self.offset.to_dict()

        position_ms = self.position_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context_uri is not UNSET:
            field_dict["context_uri"] = context_uri
        if uris is not UNSET:
            field_dict["uris"] = uris
        if offset is not UNSET:
            field_dict["offset"] = offset
        if position_ms is not UNSET:
            field_dict["position_ms"] = position_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.start_a_users_playback_body_offset import StartAUsersPlaybackBodyOffset

        d = dict(src_dict)
        context_uri = d.pop("context_uri", UNSET)

        uris = cast(list[str], d.pop("uris", UNSET))

        _offset = d.pop("offset", UNSET)
        offset: Union[Unset, StartAUsersPlaybackBodyOffset]
        if isinstance(_offset, Unset):
            offset = UNSET
        else:
            offset = StartAUsersPlaybackBodyOffset.from_dict(_offset)

        position_ms = d.pop("position_ms", UNSET)

        start_a_users_playback_body = cls(
            context_uri=context_uri,
            uris=uris,
            offset=offset,
            position_ms=position_ms,
        )

        start_a_users_playback_body.additional_properties = d
        return start_a_users_playback_body

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
