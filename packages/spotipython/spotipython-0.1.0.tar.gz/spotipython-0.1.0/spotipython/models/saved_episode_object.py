import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.episode_object import EpisodeObject


T = TypeVar("T", bound="SavedEpisodeObject")


@_attrs_define
class SavedEpisodeObject:
    """
    Attributes:
        added_at (Union[Unset, datetime.datetime]): The date and time the episode was saved.
            Timestamps are returned in ISO 8601 format as Coordinated Universal Time (UTC) with a zero offset: YYYY-MM-
            DDTHH:MM:SSZ.
        episode (Union[Unset, EpisodeObject]):
    """

    added_at: Union[Unset, datetime.datetime] = UNSET
    episode: Union[Unset, "EpisodeObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        added_at: Union[Unset, str] = UNSET
        if not isinstance(self.added_at, Unset):
            added_at = self.added_at.isoformat()

        episode: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.episode, Unset):
            episode = self.episode.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if added_at is not UNSET:
            field_dict["added_at"] = added_at
        if episode is not UNSET:
            field_dict["episode"] = episode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.episode_object import EpisodeObject

        d = dict(src_dict)
        _added_at = d.pop("added_at", UNSET)
        added_at: Union[Unset, datetime.datetime]
        if isinstance(_added_at, Unset):
            added_at = UNSET
        else:
            added_at = isoparse(_added_at)

        _episode = d.pop("episode", UNSET)
        episode: Union[Unset, EpisodeObject]
        if isinstance(_episode, Unset):
            episode = UNSET
        else:
            episode = EpisodeObject.from_dict(_episode)

        saved_episode_object = cls(
            added_at=added_at,
            episode=episode,
        )

        saved_episode_object.additional_properties = d
        return saved_episode_object

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
