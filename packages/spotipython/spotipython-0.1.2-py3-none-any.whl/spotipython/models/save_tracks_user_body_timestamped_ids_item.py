import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="SaveTracksUserBodyTimestampedIdsItem")


@_attrs_define
class SaveTracksUserBodyTimestampedIdsItem:
    """
    Attributes:
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the track.
        added_at (datetime.datetime): The timestamp when the track was added to the library. Use ISO 8601 format with
            UTC timezone (e.g., `2023-01-15T14:30:00Z`). You can specify past timestamps to insert tracks at specific
            positions in the library's chronological order. The API uses minute-level granularity for ordering, though the
            timestamp supports millisecond precision.
    """

    id: str
    added_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        added_at = self.added_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "added_at": added_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        added_at = isoparse(d.pop("added_at"))

        save_tracks_user_body_timestamped_ids_item = cls(
            id=id,
            added_at=added_at,
        )

        save_tracks_user_body_timestamped_ids_item.additional_properties = d
        return save_tracks_user_body_timestamped_ids_item

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
