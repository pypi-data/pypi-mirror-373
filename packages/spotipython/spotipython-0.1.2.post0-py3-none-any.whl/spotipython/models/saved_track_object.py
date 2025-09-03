import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="SavedTrackObject")


@_attrs_define
class SavedTrackObject:
    """
    Attributes:
        added_at (Union[Unset, datetime.datetime]): The date and time the track was saved.
            Timestamps are returned in ISO 8601 format as Coordinated Universal Time (UTC) with a zero offset: YYYY-MM-
            DDTHH:MM:SSZ.
            If the time is imprecise (for example, the date/time of an album release), an additional field indicates the
            precision; see for example, release_date in an album object.
        track (Union[Unset, TrackObject]):
    """

    added_at: Union[Unset, datetime.datetime] = UNSET
    track: Union[Unset, "TrackObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        added_at: Union[Unset, str] = UNSET
        if not isinstance(self.added_at, Unset):
            added_at = self.added_at.isoformat()

        track: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.track, Unset):
            track = self.track.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if added_at is not UNSET:
            field_dict["added_at"] = added_at
        if track is not UNSET:
            field_dict["track"] = track

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.track_object import TrackObject

        d = dict(src_dict)
        _added_at = d.pop("added_at", UNSET)
        added_at: Union[Unset, datetime.datetime]
        if isinstance(_added_at, Unset):
            added_at = UNSET
        else:
            added_at = isoparse(_added_at)

        _track = d.pop("track", UNSET)
        track: Union[Unset, TrackObject]
        if isinstance(_track, Unset):
            track = UNSET
        else:
            track = TrackObject.from_dict(_track)

        saved_track_object = cls(
            added_at=added_at,
            track=track,
        )

        saved_track_object.additional_properties = d
        return saved_track_object

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
