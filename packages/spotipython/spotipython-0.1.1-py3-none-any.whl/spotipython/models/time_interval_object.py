from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TimeIntervalObject")


@_attrs_define
class TimeIntervalObject:
    """
    Attributes:
        start (Union[Unset, float]): The starting point (in seconds) of the time interval. Example: 0.49567.
        duration (Union[Unset, float]): The duration (in seconds) of the time interval. Example: 2.18749.
        confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the interval. Example:
            0.925.
    """

    start: Union[Unset, float] = UNSET
    duration: Union[Unset, float] = UNSET
    confidence: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start = self.start

        duration = self.duration

        confidence = self.confidence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start is not UNSET:
            field_dict["start"] = start
        if duration is not UNSET:
            field_dict["duration"] = duration
        if confidence is not UNSET:
            field_dict["confidence"] = confidence

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start = d.pop("start", UNSET)

        duration = d.pop("duration", UNSET)

        confidence = d.pop("confidence", UNSET)

        time_interval_object = cls(
            start=start,
            duration=duration,
            confidence=confidence,
        )

        time_interval_object.additional_properties = d
        return time_interval_object

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
