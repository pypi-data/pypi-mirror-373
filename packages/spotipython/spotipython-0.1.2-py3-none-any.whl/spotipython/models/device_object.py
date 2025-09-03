from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceObject")


@_attrs_define
class DeviceObject:
    r"""
    Attributes:
        id (Union[None, Unset, str]): The device ID. This ID is unique and persistent to some extent. However, this is
            not guaranteed and any cached `device_id` should periodically be cleared out and refetched as necessary.
        is_active (Union[Unset, bool]): If this device is the currently active device.
        is_private_session (Union[Unset, bool]): If this device is currently in a private session.
        is_restricted (Union[Unset, bool]): Whether controlling this device is restricted. At present if this is "true"
            then no Web API commands will be accepted by this device.
        name (Union[Unset, str]): A human-readable name for the device. Some devices have a name that the user can
            configure (e.g. \"Loudest speaker\") and some devices have a generic name associated with the manufacturer or
            device model. Example: Kitchen speaker.
        type_ (Union[Unset, str]): Device type, such as "computer", "smartphone" or "speaker". Example: computer.
        volume_percent (Union[None, Unset, int]): The current volume in percent. Example: 59.
        supports_volume (Union[Unset, bool]): If this device can be used to set the volume.
    """

    id: Union[None, Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    is_private_session: Union[Unset, bool] = UNSET
    is_restricted: Union[Unset, bool] = UNSET
    name: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    volume_percent: Union[None, Unset, int] = UNSET
    supports_volume: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: Union[None, Unset, str]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        is_active = self.is_active

        is_private_session = self.is_private_session

        is_restricted = self.is_restricted

        name = self.name

        type_ = self.type_

        volume_percent: Union[None, Unset, int]
        if isinstance(self.volume_percent, Unset):
            volume_percent = UNSET
        else:
            volume_percent = self.volume_percent

        supports_volume = self.supports_volume

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if is_private_session is not UNSET:
            field_dict["is_private_session"] = is_private_session
        if is_restricted is not UNSET:
            field_dict["is_restricted"] = is_restricted
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if volume_percent is not UNSET:
            field_dict["volume_percent"] = volume_percent
        if supports_volume is not UNSET:
            field_dict["supports_volume"] = supports_volume

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        id = _parse_id(d.pop("id", UNSET))

        is_active = d.pop("is_active", UNSET)

        is_private_session = d.pop("is_private_session", UNSET)

        is_restricted = d.pop("is_restricted", UNSET)

        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        def _parse_volume_percent(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        volume_percent = _parse_volume_percent(d.pop("volume_percent", UNSET))

        supports_volume = d.pop("supports_volume", UNSET)

        device_object = cls(
            id=id,
            is_active=is_active,
            is_private_session=is_private_session,
            is_restricted=is_restricted,
            name=name,
            type_=type_,
            volume_percent=volume_percent,
            supports_volume=supports_volume,
        )

        device_object.additional_properties = d
        return device_object

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
