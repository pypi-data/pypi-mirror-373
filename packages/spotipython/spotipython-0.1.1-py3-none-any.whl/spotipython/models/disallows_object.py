from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DisallowsObject")


@_attrs_define
class DisallowsObject:
    """
    Attributes:
        interrupting_playback (Union[Unset, bool]): Interrupting playback. Optional field.
        pausing (Union[Unset, bool]): Pausing. Optional field.
        resuming (Union[Unset, bool]): Resuming. Optional field.
        seeking (Union[Unset, bool]): Seeking playback location. Optional field.
        skipping_next (Union[Unset, bool]): Skipping to the next context. Optional field.
        skipping_prev (Union[Unset, bool]): Skipping to the previous context. Optional field.
        toggling_repeat_context (Union[Unset, bool]): Toggling repeat context flag. Optional field.
        toggling_shuffle (Union[Unset, bool]): Toggling shuffle flag. Optional field.
        toggling_repeat_track (Union[Unset, bool]): Toggling repeat track flag. Optional field.
        transferring_playback (Union[Unset, bool]): Transfering playback between devices. Optional field.
    """

    interrupting_playback: Union[Unset, bool] = UNSET
    pausing: Union[Unset, bool] = UNSET
    resuming: Union[Unset, bool] = UNSET
    seeking: Union[Unset, bool] = UNSET
    skipping_next: Union[Unset, bool] = UNSET
    skipping_prev: Union[Unset, bool] = UNSET
    toggling_repeat_context: Union[Unset, bool] = UNSET
    toggling_shuffle: Union[Unset, bool] = UNSET
    toggling_repeat_track: Union[Unset, bool] = UNSET
    transferring_playback: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        interrupting_playback = self.interrupting_playback

        pausing = self.pausing

        resuming = self.resuming

        seeking = self.seeking

        skipping_next = self.skipping_next

        skipping_prev = self.skipping_prev

        toggling_repeat_context = self.toggling_repeat_context

        toggling_shuffle = self.toggling_shuffle

        toggling_repeat_track = self.toggling_repeat_track

        transferring_playback = self.transferring_playback

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if interrupting_playback is not UNSET:
            field_dict["interrupting_playback"] = interrupting_playback
        if pausing is not UNSET:
            field_dict["pausing"] = pausing
        if resuming is not UNSET:
            field_dict["resuming"] = resuming
        if seeking is not UNSET:
            field_dict["seeking"] = seeking
        if skipping_next is not UNSET:
            field_dict["skipping_next"] = skipping_next
        if skipping_prev is not UNSET:
            field_dict["skipping_prev"] = skipping_prev
        if toggling_repeat_context is not UNSET:
            field_dict["toggling_repeat_context"] = toggling_repeat_context
        if toggling_shuffle is not UNSET:
            field_dict["toggling_shuffle"] = toggling_shuffle
        if toggling_repeat_track is not UNSET:
            field_dict["toggling_repeat_track"] = toggling_repeat_track
        if transferring_playback is not UNSET:
            field_dict["transferring_playback"] = transferring_playback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        interrupting_playback = d.pop("interrupting_playback", UNSET)

        pausing = d.pop("pausing", UNSET)

        resuming = d.pop("resuming", UNSET)

        seeking = d.pop("seeking", UNSET)

        skipping_next = d.pop("skipping_next", UNSET)

        skipping_prev = d.pop("skipping_prev", UNSET)

        toggling_repeat_context = d.pop("toggling_repeat_context", UNSET)

        toggling_shuffle = d.pop("toggling_shuffle", UNSET)

        toggling_repeat_track = d.pop("toggling_repeat_track", UNSET)

        transferring_playback = d.pop("transferring_playback", UNSET)

        disallows_object = cls(
            interrupting_playback=interrupting_playback,
            pausing=pausing,
            resuming=resuming,
            seeking=seeking,
            skipping_next=skipping_next,
            skipping_prev=skipping_prev,
            toggling_repeat_context=toggling_repeat_context,
            toggling_shuffle=toggling_shuffle,
            toggling_repeat_track=toggling_repeat_track,
            transferring_playback=transferring_playback,
        )

        disallows_object.additional_properties = d
        return disallows_object

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
