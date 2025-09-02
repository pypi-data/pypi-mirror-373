from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.save_tracks_user_body_timestamped_ids_item import SaveTracksUserBodyTimestampedIdsItem


T = TypeVar("T", bound="SaveTracksUserBody")


@_attrs_define
class SaveTracksUserBody:
    """
    Attributes:
        ids (Union[Unset, list[str]]): A JSON array of the [Spotify IDs](/documentation/web-api/concepts/spotify-uris-
            ids). For example: `["4iV5W9uYEdYUVa79Axb7Rh", "1301WleyT98MSxVHPZCA6M"]`<br/>A maximum of 50 items can be
            specified in one request. _**Note**: if the `timestamped_ids` is present in the body, any IDs listed in the
            query parameters (deprecated) or the `ids` field in the body will be ignored._
        timestamped_ids (Union[Unset, list['SaveTracksUserBodyTimestampedIdsItem']]): A JSON array of objects containing
            track IDs with their corresponding timestamps. Each object must include a track ID and an `added_at` timestamp.
            This allows you to specify when tracks were added to maintain a specific chronological order in the user's
            library.<br/>A maximum of 50 items can be specified in one request. _**Note**: if the `timestamped_ids` is
            present in the body, any IDs listed in the query parameters (deprecated) or the `ids` field in the body will be
            ignored._
    """

    ids: Union[Unset, list[str]] = UNSET
    timestamped_ids: Union[Unset, list["SaveTracksUserBodyTimestampedIdsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.ids, Unset):
            ids = self.ids

        timestamped_ids: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.timestamped_ids, Unset):
            timestamped_ids = []
            for timestamped_ids_item_data in self.timestamped_ids:
                timestamped_ids_item = timestamped_ids_item_data.to_dict()
                timestamped_ids.append(timestamped_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ids is not UNSET:
            field_dict["ids"] = ids
        if timestamped_ids is not UNSET:
            field_dict["timestamped_ids"] = timestamped_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.save_tracks_user_body_timestamped_ids_item import SaveTracksUserBodyTimestampedIdsItem

        d = dict(src_dict)
        ids = cast(list[str], d.pop("ids", UNSET))

        timestamped_ids = []
        _timestamped_ids = d.pop("timestamped_ids", UNSET)
        for timestamped_ids_item_data in _timestamped_ids or []:
            timestamped_ids_item = SaveTracksUserBodyTimestampedIdsItem.from_dict(timestamped_ids_item_data)

            timestamped_ids.append(timestamped_ids_item)

        save_tracks_user_body = cls(
            ids=ids,
            timestamped_ids=timestamped_ids,
        )

        save_tracks_user_body.additional_properties = d
        return save_tracks_user_body

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
