from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResumePointObject")


@_attrs_define
class ResumePointObject:
    """
    Attributes:
        fully_played (Union[Unset, bool]): Whether or not the episode has been fully played by the user.
        resume_position_ms (Union[Unset, int]): The user's most recent position in the episode in milliseconds.
    """

    fully_played: Union[Unset, bool] = UNSET
    resume_position_ms: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fully_played = self.fully_played

        resume_position_ms = self.resume_position_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fully_played is not UNSET:
            field_dict["fully_played"] = fully_played
        if resume_position_ms is not UNSET:
            field_dict["resume_position_ms"] = resume_position_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fully_played = d.pop("fully_played", UNSET)

        resume_position_ms = d.pop("resume_position_ms", UNSET)

        resume_point_object = cls(
            fully_played=fully_played,
            resume_position_ms=resume_position_ms,
        )

        resume_point_object.additional_properties = d
        return resume_point_object

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
