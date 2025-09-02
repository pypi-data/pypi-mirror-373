from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.image_object import ImageObject


T = TypeVar("T", bound="CategoryObject")


@_attrs_define
class CategoryObject:
    """
    Attributes:
        href (str): A link to the Web API endpoint returning full details of the category.
        icons (list['ImageObject']): The category icon, in various sizes.
        id (str): The [Spotify category ID](/documentation/web-api/concepts/spotify-uris-ids) of the category.
             Example: equal.
        name (str): The name of the category.
             Example: EQUAL.
    """

    href: str
    icons: list["ImageObject"]
    id: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        href = self.href

        icons = []
        for icons_item_data in self.icons:
            icons_item = icons_item_data.to_dict()
            icons.append(icons_item)

        id = self.id

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "href": href,
                "icons": icons,
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.image_object import ImageObject

        d = dict(src_dict)
        href = d.pop("href")

        icons = []
        _icons = d.pop("icons")
        for icons_item_data in _icons:
            icons_item = ImageObject.from_dict(icons_item_data)

            icons.append(icons_item)

        id = d.pop("id")

        name = d.pop("name")

        category_object = cls(
            href=href,
            icons=icons,
            id=id,
            name=name,
        )

        category_object.additional_properties = d
        return category_object

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
