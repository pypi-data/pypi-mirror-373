import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_object import ContextObject
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="PlayHistoryObject")


@_attrs_define
class PlayHistoryObject:
    """
    Attributes:
        context (Union[Unset, ContextObject]):
        played_at (Union[Unset, datetime.datetime]): The date and time the track was played.
        track (Union[Unset, TrackObject]):
    """

    context: Union[Unset, "ContextObject"] = UNSET
    played_at: Union[Unset, datetime.datetime] = UNSET
    track: Union[Unset, "TrackObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        context: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        played_at: Union[Unset, str] = UNSET
        if not isinstance(self.played_at, Unset):
            played_at = self.played_at.isoformat()

        track: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.track, Unset):
            track = self.track.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["context"] = context
        if played_at is not UNSET:
            field_dict["played_at"] = played_at
        if track is not UNSET:
            field_dict["track"] = track

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_object import ContextObject
        from ..models.track_object import TrackObject

        d = dict(src_dict)
        _context = d.pop("context", UNSET)
        context: Union[Unset, ContextObject]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ContextObject.from_dict(_context)

        _played_at = d.pop("played_at", UNSET)
        played_at: Union[Unset, datetime.datetime]
        if isinstance(_played_at, Unset):
            played_at = UNSET
        else:
            played_at = isoparse(_played_at)

        _track = d.pop("track", UNSET)
        track: Union[Unset, TrackObject]
        if isinstance(_track, Unset):
            track = UNSET
        else:
            track = TrackObject.from_dict(_track)

        play_history_object = cls(
            context=context,
            played_at=played_at,
            track=track,
        )

        play_history_object.additional_properties = d
        return play_history_object

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
