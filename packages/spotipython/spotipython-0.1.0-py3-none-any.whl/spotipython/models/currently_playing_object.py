from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_object import ContextObject
    from ..models.episode_object import EpisodeObject
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="CurrentlyPlayingObject")


@_attrs_define
class CurrentlyPlayingObject:
    """
    Attributes:
        context (Union[Unset, ContextObject]):
        currently_playing_type (Union[Unset, str]): The object type of the currently playing item. Can be one of
            `track`, `episode`, `ad` or `unknown`.
        is_playing (Union[Unset, bool]): If something is currently playing, return `true`.
        item (Union['EpisodeObject', 'TrackObject', Unset]): The currently playing track or episode. Can be `null`.
        progress_ms (Union[Unset, int]): Progress into the currently playing track or episode. Can be `null`.
        timestamp (Union[Unset, int]): Unix Millisecond Timestamp when data was fetched
    """

    context: Union[Unset, "ContextObject"] = UNSET
    currently_playing_type: Union[Unset, str] = UNSET
    is_playing: Union[Unset, bool] = UNSET
    item: Union["EpisodeObject", "TrackObject", Unset] = UNSET
    progress_ms: Union[Unset, int] = UNSET
    timestamp: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.track_object import TrackObject

        context: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        currently_playing_type = self.currently_playing_type

        is_playing = self.is_playing

        item: Union[Unset, dict[str, Any]]
        if isinstance(self.item, Unset):
            item = UNSET
        elif isinstance(self.item, TrackObject):
            item = self.item.to_dict()
        else:
            item = self.item.to_dict()

        progress_ms = self.progress_ms

        timestamp = self.timestamp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["context"] = context
        if currently_playing_type is not UNSET:
            field_dict["currently_playing_type"] = currently_playing_type
        if is_playing is not UNSET:
            field_dict["is_playing"] = is_playing
        if item is not UNSET:
            field_dict["item"] = item
        if progress_ms is not UNSET:
            field_dict["progress_ms"] = progress_ms
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_object import ContextObject
        from ..models.episode_object import EpisodeObject
        from ..models.track_object import TrackObject

        d = dict(src_dict)
        _context = d.pop("context", UNSET)
        context: Union[Unset, ContextObject]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ContextObject.from_dict(_context)

        currently_playing_type = d.pop("currently_playing_type", UNSET)

        is_playing = d.pop("is_playing", UNSET)

        def _parse_item(data: object) -> Union["EpisodeObject", "TrackObject", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                item_type_0 = TrackObject.from_dict(data)

                return item_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            item_type_1 = EpisodeObject.from_dict(data)

            return item_type_1

        item = _parse_item(d.pop("item", UNSET))

        progress_ms = d.pop("progress_ms", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        currently_playing_object = cls(
            context=context,
            currently_playing_type=currently_playing_type,
            is_playing=is_playing,
            item=item,
            progress_ms=progress_ms,
            timestamp=timestamp,
        )

        currently_playing_object.additional_properties = d
        return currently_playing_object

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
