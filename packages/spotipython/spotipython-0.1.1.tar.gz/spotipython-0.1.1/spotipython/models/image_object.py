from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ImageObject")


@_attrs_define
class ImageObject:
    """
    Attributes:
        url (str): The source URL of the image.
             Example: https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228
            .
        height (Union[None, int]): The image height in pixels.
             Example: 300.
        width (Union[None, int]): The image width in pixels.
             Example: 300.
    """

    url: str
    height: Union[None, int]
    width: Union[None, int]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        height: Union[None, int]
        height = self.height

        width: Union[None, int]
        width = self.width

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "height": height,
                "width": width,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        def _parse_height(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        height = _parse_height(d.pop("height"))

        def _parse_width(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        width = _parse_width(d.pop("width"))

        image_object = cls(
            url=url,
            height=height,
            width=width,
        )

        image_object.additional_properties = d
        return image_object

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
