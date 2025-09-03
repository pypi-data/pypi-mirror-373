from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.episode_object import EpisodeObject
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="QueueObject")


@_attrs_define
class QueueObject:
    """
    Attributes:
        currently_playing (Union['EpisodeObject', 'TrackObject', Unset]): The currently playing track or episode. Can be
            `null`.
        queue (Union[Unset, list[Union['EpisodeObject', 'TrackObject']]]): The tracks or episodes in the queue. Can be
            empty.
    """

    currently_playing: Union["EpisodeObject", "TrackObject", Unset] = UNSET
    queue: Union[Unset, list[Union["EpisodeObject", "TrackObject"]]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.track_object import TrackObject

        currently_playing: Union[Unset, dict[str, Any]]
        if isinstance(self.currently_playing, Unset):
            currently_playing = UNSET
        elif isinstance(self.currently_playing, TrackObject):
            currently_playing = self.currently_playing.to_dict()
        else:
            currently_playing = self.currently_playing.to_dict()

        queue: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.queue, Unset):
            queue = []
            for queue_item_data in self.queue:
                queue_item: dict[str, Any]
                if isinstance(queue_item_data, TrackObject):
                    queue_item = queue_item_data.to_dict()
                else:
                    queue_item = queue_item_data.to_dict()

                queue.append(queue_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if currently_playing is not UNSET:
            field_dict["currently_playing"] = currently_playing
        if queue is not UNSET:
            field_dict["queue"] = queue

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.episode_object import EpisodeObject
        from ..models.track_object import TrackObject

        d = dict(src_dict)

        def _parse_currently_playing(data: object) -> Union["EpisodeObject", "TrackObject", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                currently_playing_type_0 = TrackObject.from_dict(data)

                return currently_playing_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            currently_playing_type_1 = EpisodeObject.from_dict(data)

            return currently_playing_type_1

        currently_playing = _parse_currently_playing(d.pop("currently_playing", UNSET))

        queue = []
        _queue = d.pop("queue", UNSET)
        for queue_item_data in _queue or []:

            def _parse_queue_item(data: object) -> Union["EpisodeObject", "TrackObject"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    queue_item_type_0 = TrackObject.from_dict(data)

                    return queue_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                queue_item_type_1 = EpisodeObject.from_dict(data)

                return queue_item_type_1

            queue_item = _parse_queue_item(queue_item_data)

            queue.append(queue_item)

        queue_object = cls(
            currently_playing=currently_playing,
            queue=queue,
        )

        queue_object.additional_properties = d
        return queue_object

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
