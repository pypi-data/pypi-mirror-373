from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddTracksToPlaylistBody")


@_attrs_define
class AddTracksToPlaylistBody:
    """
    Attributes:
        uris (Union[Unset, list[str]]): A JSON array of the [Spotify URIs](/documentation/web-api/concepts/spotify-uris-
            ids) to add. For example: `{"uris":
            ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh","spotify:track:1301WleyT98MSxVHPZCA6M",
            "spotify:episode:512ojhOuo1ktJprKbVcKyQ"]}`<br/>A maximum of 100 items can be added in one request. _**Note**:
            if the `uris` parameter is present in the query string, any URIs listed here in the body will be ignored._
        position (Union[Unset, int]): The position to insert the items, a zero-based index. For example, to insert the
            items in the first position: `position=0` ; to insert the items in the third position: `position=2`. If omitted,
            the items will be appended to the playlist. Items are added in the order they appear in the uris array. For
            example: `{"uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh","spotify:track:1301WleyT98MSxVHPZCA6M"], "position":
            3}`
    """

    uris: Union[Unset, list[str]] = UNSET
    position: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uris: Union[Unset, list[str]] = UNSET
        if not isinstance(self.uris, Unset):
            uris = self.uris

        position = self.position

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uris is not UNSET:
            field_dict["uris"] = uris
        if position is not UNSET:
            field_dict["position"] = position

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uris = cast(list[str], d.pop("uris", UNSET))

        position = d.pop("position", UNSET)

        add_tracks_to_playlist_body = cls(
            uris=uris,
            position=position,
        )

        add_tracks_to_playlist_body.additional_properties = d
        return add_tracks_to_playlist_body

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
