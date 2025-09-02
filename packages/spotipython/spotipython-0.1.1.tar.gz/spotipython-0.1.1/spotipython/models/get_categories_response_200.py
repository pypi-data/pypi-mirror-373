from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_categories_response_200_categories import GetCategoriesResponse200Categories


T = TypeVar("T", bound="GetCategoriesResponse200")


@_attrs_define
class GetCategoriesResponse200:
    """
    Attributes:
        categories (GetCategoriesResponse200Categories):
    """

    categories: "GetCategoriesResponse200Categories"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        categories = self.categories.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "categories": categories,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_categories_response_200_categories import GetCategoriesResponse200Categories

        d = dict(src_dict)
        categories = GetCategoriesResponse200Categories.from_dict(d.pop("categories"))

        get_categories_response_200 = cls(
            categories=categories,
        )

        get_categories_response_200.additional_properties = d
        return get_categories_response_200

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
