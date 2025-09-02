from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.player_error_reasons import PlayerErrorReasons
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlayerErrorObject")


@_attrs_define
class PlayerErrorObject:
    """
    Attributes:
        message (Union[Unset, str]): A short description of the cause of the error.
        reason (Union[Unset, PlayerErrorReasons]): * `NO_PREV_TRACK` - The command requires a previous track, but there
            is none in the context.
            * `NO_NEXT_TRACK` - The command requires a next track, but there is none in the context.
            * `NO_SPECIFIC_TRACK` - The requested track does not exist.
            * `ALREADY_PAUSED` - The command requires playback to not be paused.
            * `NOT_PAUSED` - The command requires playback to be paused.
            * `NOT_PLAYING_LOCALLY` - The command requires playback on the local device.
            * `NOT_PLAYING_TRACK` - The command requires that a track is currently playing.
            * `NOT_PLAYING_CONTEXT` - The command requires that a context is currently playing.
            * `ENDLESS_CONTEXT` - The shuffle command cannot be applied on an endless context.
            * `CONTEXT_DISALLOW` - The command could not be performed on the context.
            * `ALREADY_PLAYING` - The track should not be restarted if the same track and context is already playing, and
            there is a resume point.
            * `RATE_LIMITED` - The user is rate limited due to too frequent track play, also known as cat-on-the-keyboard
            spamming.
            * `REMOTE_CONTROL_DISALLOW` - The context cannot be remote-controlled.
            * `DEVICE_NOT_CONTROLLABLE` - Not possible to remote control the device.
            * `VOLUME_CONTROL_DISALLOW` - Not possible to remote control the device's volume.
            * `NO_ACTIVE_DEVICE` - Requires an active device and the user has none.
            * `PREMIUM_REQUIRED` - The request is prohibited for non-premium users.
            * `UNKNOWN` - Certain actions are restricted because of unknown reasons.
        status (Union[Unset, int]): The HTTP status code. Either `404 NOT FOUND` or `403 FORBIDDEN`.  Also returned in
            the response header.
    """

    message: Union[Unset, str] = UNSET
    reason: Union[Unset, PlayerErrorReasons] = UNSET
    status: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        reason: Union[Unset, str] = UNSET
        if not isinstance(self.reason, Unset):
            reason = self.reason.value

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message
        if reason is not UNSET:
            field_dict["reason"] = reason
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message", UNSET)

        _reason = d.pop("reason", UNSET)
        reason: Union[Unset, PlayerErrorReasons]
        if isinstance(_reason, Unset):
            reason = UNSET
        else:
            reason = PlayerErrorReasons(_reason)

        status = d.pop("status", UNSET)

        player_error_object = cls(
            message=message,
            reason=reason,
            status=status,
        )

        player_error_object.additional_properties = d
        return player_error_object

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
