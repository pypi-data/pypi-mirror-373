from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.chapter_object import ChapterObject


T = TypeVar("T", bound="GetSeveralChaptersResponse200")


@_attrs_define
class GetSeveralChaptersResponse200:
    """
    Attributes:
        chapters (list['ChapterObject']):
    """

    chapters: list["ChapterObject"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chapters = []
        for chapters_item_data in self.chapters:
            chapters_item = chapters_item_data.to_dict()
            chapters.append(chapters_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chapters": chapters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chapter_object import ChapterObject

        d = dict(src_dict)
        chapters = []
        _chapters = d.pop("chapters")
        for chapters_item_data in _chapters:
            chapters_item = ChapterObject.from_dict(chapters_item_data)

            chapters.append(chapters_item)

        get_several_chapters_response_200 = cls(
            chapters=chapters,
        )

        get_several_chapters_response_200.additional_properties = d
        return get_several_chapters_response_200

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
