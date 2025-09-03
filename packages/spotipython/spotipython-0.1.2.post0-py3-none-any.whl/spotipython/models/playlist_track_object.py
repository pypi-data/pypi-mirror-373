import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.episode_object import EpisodeObject
    from ..models.playlist_user_object import PlaylistUserObject
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="PlaylistTrackObject")


@_attrs_define
class PlaylistTrackObject:
    """
    Attributes:
        added_at (Union[Unset, datetime.datetime]): The date and time the track or episode was added. _**Note**: some
            very old playlists may return `null` in this field._
        added_by (Union[Unset, PlaylistUserObject]):
        is_local (Union[Unset, bool]): Whether this track or episode is a [local file](/documentation/web-
            api/concepts/playlists/#local-files) or not.
        track (Union['EpisodeObject', 'TrackObject', Unset]): Information about the track or episode.
    """

    added_at: Union[Unset, datetime.datetime] = UNSET
    added_by: Union[Unset, "PlaylistUserObject"] = UNSET
    is_local: Union[Unset, bool] = UNSET
    track: Union["EpisodeObject", "TrackObject", Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.track_object import TrackObject

        added_at: Union[Unset, str] = UNSET
        if not isinstance(self.added_at, Unset):
            added_at = self.added_at.isoformat()

        added_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.added_by, Unset):
            added_by = self.added_by.to_dict()

        is_local = self.is_local

        track: Union[Unset, dict[str, Any]]
        if isinstance(self.track, Unset):
            track = UNSET
        elif isinstance(self.track, TrackObject):
            track = self.track.to_dict()
        else:
            track = self.track.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if added_at is not UNSET:
            field_dict["added_at"] = added_at
        if added_by is not UNSET:
            field_dict["added_by"] = added_by
        if is_local is not UNSET:
            field_dict["is_local"] = is_local
        if track is not UNSET:
            field_dict["track"] = track

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.episode_object import EpisodeObject
        from ..models.playlist_user_object import PlaylistUserObject
        from ..models.track_object import TrackObject

        d = dict(src_dict)
        _added_at = d.pop("added_at", UNSET)
        added_at: Union[Unset, datetime.datetime]
        if isinstance(_added_at, Unset):
            added_at = UNSET
        else:
            added_at = isoparse(_added_at)

        _added_by = d.pop("added_by", UNSET)
        added_by: Union[Unset, PlaylistUserObject]
        if isinstance(_added_by, Unset):
            added_by = UNSET
        else:
            added_by = PlaylistUserObject.from_dict(_added_by)

        is_local = d.pop("is_local", UNSET)

        def _parse_track(data: object) -> Union["EpisodeObject", "TrackObject", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                track_type_0 = TrackObject.from_dict(data)

                return track_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            track_type_1 = EpisodeObject.from_dict(data)

            return track_type_1

        track = _parse_track(d.pop("track", UNSET))

        playlist_track_object = cls(
            added_at=added_at,
            added_by=added_by,
            is_local=is_local,
            track=track,
        )

        playlist_track_object.additional_properties = d
        return playlist_track_object

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
