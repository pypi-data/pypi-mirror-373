from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.simplified_show_object import SimplifiedShowObject


T = TypeVar("T", bound="GetMultipleShowsResponse200")


@_attrs_define
class GetMultipleShowsResponse200:
    """
    Attributes:
        shows (list['SimplifiedShowObject']):
    """

    shows: list["SimplifiedShowObject"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        shows = []
        for shows_item_data in self.shows:
            shows_item = shows_item_data.to_dict()
            shows.append(shows_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "shows": shows,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.simplified_show_object import SimplifiedShowObject

        d = dict(src_dict)
        shows = []
        _shows = d.pop("shows")
        for shows_item_data in _shows:
            shows_item = SimplifiedShowObject.from_dict(shows_item_data)

            shows.append(shows_item)

        get_multiple_shows_response_200 = cls(
            shows=shows,
        )

        get_multiple_shows_response_200.additional_properties = d
        return get_multiple_shows_response_200

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
