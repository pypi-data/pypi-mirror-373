from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.audiobook_object import AudiobookObject


T = TypeVar("T", bound="GetMultipleAudiobooksResponse200")


@_attrs_define
class GetMultipleAudiobooksResponse200:
    """
    Attributes:
        audiobooks (list['AudiobookObject']):
    """

    audiobooks: list["AudiobookObject"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audiobooks = []
        for audiobooks_item_data in self.audiobooks:
            audiobooks_item = audiobooks_item_data.to_dict()
            audiobooks.append(audiobooks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "audiobooks": audiobooks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audiobook_object import AudiobookObject

        d = dict(src_dict)
        audiobooks = []
        _audiobooks = d.pop("audiobooks")
        for audiobooks_item_data in _audiobooks:
            audiobooks_item = AudiobookObject.from_dict(audiobooks_item_data)

            audiobooks.append(audiobooks_item)

        get_multiple_audiobooks_response_200 = cls(
            audiobooks=audiobooks,
        )

        get_multiple_audiobooks_response_200.additional_properties = d
        return get_multiple_audiobooks_response_200

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
