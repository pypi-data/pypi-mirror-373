import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.simplified_show_object import SimplifiedShowObject


T = TypeVar("T", bound="SavedShowObject")


@_attrs_define
class SavedShowObject:
    """
    Attributes:
        added_at (Union[Unset, datetime.datetime]): The date and time the show was saved.
            Timestamps are returned in ISO 8601 format as Coordinated Universal Time (UTC) with a zero offset: YYYY-MM-
            DDTHH:MM:SSZ.
            If the time is imprecise (for example, the date/time of an album release), an additional field indicates the
            precision; see for example, release_date in an album object.
        show (Union[Unset, SimplifiedShowObject]):
    """

    added_at: Union[Unset, datetime.datetime] = UNSET
    show: Union[Unset, "SimplifiedShowObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        added_at: Union[Unset, str] = UNSET
        if not isinstance(self.added_at, Unset):
            added_at = self.added_at.isoformat()

        show: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.show, Unset):
            show = self.show.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if added_at is not UNSET:
            field_dict["added_at"] = added_at
        if show is not UNSET:
            field_dict["show"] = show

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.simplified_show_object import SimplifiedShowObject

        d = dict(src_dict)
        _added_at = d.pop("added_at", UNSET)
        added_at: Union[Unset, datetime.datetime]
        if isinstance(_added_at, Unset):
            added_at = UNSET
        else:
            added_at = isoparse(_added_at)

        _show = d.pop("show", UNSET)
        show: Union[Unset, SimplifiedShowObject]
        if isinstance(_show, Unset):
            show = UNSET
        else:
            show = SimplifiedShowObject.from_dict(_show)

        saved_show_object = cls(
            added_at=added_at,
            show=show,
        )

        saved_show_object.additional_properties = d
        return saved_show_object

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
