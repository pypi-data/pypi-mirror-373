from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReorderOrReplacePlaylistsTracksBody")


@_attrs_define
class ReorderOrReplacePlaylistsTracksBody:
    """
    Example:
        {'range_start': 1, 'insert_before': 3, 'range_length': 2}

    Attributes:
        uris (Union[Unset, list[str]]):
        range_start (Union[Unset, int]): The position of the first item to be reordered.
        insert_before (Union[Unset, int]): The position where the items should be inserted.<br/>To reorder the items to
            the end of the playlist, simply set _insert_before_ to the position after the last item.<br/>Examples:<br/>To
            reorder the first item to the last position in a playlist with 10 items, set _range_start_ to 0, and
            _insert_before_ to 10.<br/>To reorder the last item in a playlist with 10 items to the start of the playlist,
            set _range_start_ to 9, and _insert_before_ to 0.
        range_length (Union[Unset, int]): The amount of items to be reordered. Defaults to 1 if not set.<br/>The range
            of items to be reordered begins from the _range_start_ position, and includes the _range_length_ subsequent
            items.<br/>Example:<br/>To move the items at index 9-10 to the start of the playlist, _range_start_ is set to 9,
            and _range_length_ is set to 2.
        snapshot_id (Union[Unset, str]): The playlist's snapshot ID against which you want to make the changes.
    """

    uris: Union[Unset, list[str]] = UNSET
    range_start: Union[Unset, int] = UNSET
    insert_before: Union[Unset, int] = UNSET
    range_length: Union[Unset, int] = UNSET
    snapshot_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uris: Union[Unset, list[str]] = UNSET
        if not isinstance(self.uris, Unset):
            uris = self.uris

        range_start = self.range_start

        insert_before = self.insert_before

        range_length = self.range_length

        snapshot_id = self.snapshot_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uris is not UNSET:
            field_dict["uris"] = uris
        if range_start is not UNSET:
            field_dict["range_start"] = range_start
        if insert_before is not UNSET:
            field_dict["insert_before"] = insert_before
        if range_length is not UNSET:
            field_dict["range_length"] = range_length
        if snapshot_id is not UNSET:
            field_dict["snapshot_id"] = snapshot_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uris = cast(list[str], d.pop("uris", UNSET))

        range_start = d.pop("range_start", UNSET)

        insert_before = d.pop("insert_before", UNSET)

        range_length = d.pop("range_length", UNSET)

        snapshot_id = d.pop("snapshot_id", UNSET)

        reorder_or_replace_playlists_tracks_body = cls(
            uris=uris,
            range_start=range_start,
            insert_before=insert_before,
            range_length=range_length,
            snapshot_id=snapshot_id,
        )

        reorder_or_replace_playlists_tracks_body.additional_properties = d
        return reorder_or_replace_playlists_tracks_body

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
