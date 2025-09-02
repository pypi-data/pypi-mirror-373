from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TransferAUsersPlaybackBody")


@_attrs_define
class TransferAUsersPlaybackBody:
    """
    Example:
        {'device_ids': ['74ASZWbe4lXaubB36ztrGX']}

    Attributes:
        device_ids (list[str]): A JSON array containing the ID of the device on which playback should be
            started/transferred.<br/>For example:`{device_ids:["74ASZWbe4lXaubB36ztrGX"]}`<br/>_**Note**: Although an array
            is accepted, only a single device_id is currently supported. Supplying more than one will return `400 Bad
            Request`_
        play (Union[Unset, bool]): **true**: ensure playback happens on new device.<br/>**false** or not provided: keep
            the current playback state.
    """

    device_ids: list[str]
    play: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_ids = self.device_ids

        play = self.play

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_ids": device_ids,
            }
        )
        if play is not UNSET:
            field_dict["play"] = play

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_ids = cast(list[str], d.pop("device_ids"))

        play = d.pop("play", UNSET)

        transfer_a_users_playback_body = cls(
            device_ids=device_ids,
            play=play,
        )

        transfer_a_users_playback_body.additional_properties = d
        return transfer_a_users_playback_body

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
