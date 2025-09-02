from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.audio_features_object import AudioFeaturesObject


T = TypeVar("T", bound="GetSeveralAudioFeaturesResponse200")


@_attrs_define
class GetSeveralAudioFeaturesResponse200:
    """
    Attributes:
        audio_features (list['AudioFeaturesObject']):
    """

    audio_features: list["AudioFeaturesObject"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audio_features = []
        for audio_features_item_data in self.audio_features:
            audio_features_item = audio_features_item_data.to_dict()
            audio_features.append(audio_features_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "audio_features": audio_features,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audio_features_object import AudioFeaturesObject

        d = dict(src_dict)
        audio_features = []
        _audio_features = d.pop("audio_features")
        for audio_features_item_data in _audio_features:
            audio_features_item = AudioFeaturesObject.from_dict(audio_features_item_data)

            audio_features.append(audio_features_item)

        get_several_audio_features_response_200 = cls(
            audio_features=audio_features,
        )

        get_several_audio_features_response_200.additional_properties = d
        return get_several_audio_features_response_200

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
