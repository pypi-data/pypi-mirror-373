from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_object import ContextObject
    from ..models.device_object import DeviceObject
    from ..models.disallows_object import DisallowsObject
    from ..models.episode_object import EpisodeObject
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="CurrentlyPlayingContextObject")


@_attrs_define
class CurrentlyPlayingContextObject:
    """
    Attributes:
        device (Union[Unset, DeviceObject]):
        repeat_state (Union[Unset, str]): off, track, context
        shuffle_state (Union[Unset, bool]): If shuffle is on or off.
        context (Union[Unset, ContextObject]):
        timestamp (Union[Unset, int]): Unix Millisecond Timestamp when playback state was last changed (play, pause,
            skip, scrub, new song, etc.).
        progress_ms (Union[Unset, int]): Progress into the currently playing track or episode. Can be `null`.
        is_playing (Union[Unset, bool]): If something is currently playing, return `true`.
        item (Union['EpisodeObject', 'TrackObject', Unset]): The currently playing track or episode. Can be `null`.
        currently_playing_type (Union[Unset, str]): The object type of the currently playing item. Can be one of
            `track`, `episode`, `ad` or `unknown`.
        actions (Union[Unset, DisallowsObject]):
    """

    device: Union[Unset, "DeviceObject"] = UNSET
    repeat_state: Union[Unset, str] = UNSET
    shuffle_state: Union[Unset, bool] = UNSET
    context: Union[Unset, "ContextObject"] = UNSET
    timestamp: Union[Unset, int] = UNSET
    progress_ms: Union[Unset, int] = UNSET
    is_playing: Union[Unset, bool] = UNSET
    item: Union["EpisodeObject", "TrackObject", Unset] = UNSET
    currently_playing_type: Union[Unset, str] = UNSET
    actions: Union[Unset, "DisallowsObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.track_object import TrackObject

        device: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.device, Unset):
            device = self.device.to_dict()

        repeat_state = self.repeat_state

        shuffle_state = self.shuffle_state

        context: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        timestamp = self.timestamp

        progress_ms = self.progress_ms

        is_playing = self.is_playing

        item: Union[Unset, dict[str, Any]]
        if isinstance(self.item, Unset):
            item = UNSET
        elif isinstance(self.item, TrackObject):
            item = self.item.to_dict()
        else:
            item = self.item.to_dict()

        currently_playing_type = self.currently_playing_type

        actions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device is not UNSET:
            field_dict["device"] = device
        if repeat_state is not UNSET:
            field_dict["repeat_state"] = repeat_state
        if shuffle_state is not UNSET:
            field_dict["shuffle_state"] = shuffle_state
        if context is not UNSET:
            field_dict["context"] = context
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if progress_ms is not UNSET:
            field_dict["progress_ms"] = progress_ms
        if is_playing is not UNSET:
            field_dict["is_playing"] = is_playing
        if item is not UNSET:
            field_dict["item"] = item
        if currently_playing_type is not UNSET:
            field_dict["currently_playing_type"] = currently_playing_type
        if actions is not UNSET:
            field_dict["actions"] = actions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_object import ContextObject
        from ..models.device_object import DeviceObject
        from ..models.disallows_object import DisallowsObject
        from ..models.episode_object import EpisodeObject
        from ..models.track_object import TrackObject

        d = dict(src_dict)
        _device = d.pop("device", UNSET)
        device: Union[Unset, DeviceObject]
        if isinstance(_device, Unset):
            device = UNSET
        else:
            device = DeviceObject.from_dict(_device)

        repeat_state = d.pop("repeat_state", UNSET)

        shuffle_state = d.pop("shuffle_state", UNSET)

        _context = d.pop("context", UNSET)
        context: Union[Unset, ContextObject]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = ContextObject.from_dict(_context)

        timestamp = d.pop("timestamp", UNSET)

        progress_ms = d.pop("progress_ms", UNSET)

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

        currently_playing_type = d.pop("currently_playing_type", UNSET)

        _actions = d.pop("actions", UNSET)
        actions: Union[Unset, DisallowsObject]
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = DisallowsObject.from_dict(_actions)

        currently_playing_context_object = cls(
            device=device,
            repeat_state=repeat_state,
            shuffle_state=shuffle_state,
            context=context,
            timestamp=timestamp,
            progress_ms=progress_ms,
            is_playing=is_playing,
            item=item,
            currently_playing_type=currently_playing_type,
            actions=actions,
        )

        currently_playing_context_object.additional_properties = d
        return currently_playing_context_object

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
