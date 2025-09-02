from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.remove_tracks_playlist_body_tracks_item import RemoveTracksPlaylistBodyTracksItem


T = TypeVar("T", bound="RemoveTracksPlaylistBody")


@_attrs_define
class RemoveTracksPlaylistBody:
    """
    Attributes:
        tracks (list['RemoveTracksPlaylistBodyTracksItem']): An array of objects containing [Spotify
            URIs](/documentation/web-api/concepts/spotify-uris-ids) of the tracks or episodes to remove.
            For example: `{ "tracks": [{ "uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh" },{ "uri":
            "spotify:track:1301WleyT98MSxVHPZCA6M" }] }`. A maximum of 100 objects can be sent at once.
        snapshot_id (Union[Unset, str]): The playlist's snapshot ID against which you want to make the changes.
            The API will validate that the specified items exist and in the specified positions and make the changes,
            even if more recent changes have been made to the playlist.
    """

    tracks: list["RemoveTracksPlaylistBodyTracksItem"]
    snapshot_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tracks = []
        for tracks_item_data in self.tracks:
            tracks_item = tracks_item_data.to_dict()
            tracks.append(tracks_item)

        snapshot_id = self.snapshot_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tracks": tracks,
            }
        )
        if snapshot_id is not UNSET:
            field_dict["snapshot_id"] = snapshot_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.remove_tracks_playlist_body_tracks_item import RemoveTracksPlaylistBodyTracksItem

        d = dict(src_dict)
        tracks = []
        _tracks = d.pop("tracks")
        for tracks_item_data in _tracks:
            tracks_item = RemoveTracksPlaylistBodyTracksItem.from_dict(tracks_item_data)

            tracks.append(tracks_item)

        snapshot_id = d.pop("snapshot_id", UNSET)

        remove_tracks_playlist_body = cls(
            tracks=tracks,
            snapshot_id=snapshot_id,
        )

        remove_tracks_playlist_body.additional_properties = d
        return remove_tracks_playlist_body

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
