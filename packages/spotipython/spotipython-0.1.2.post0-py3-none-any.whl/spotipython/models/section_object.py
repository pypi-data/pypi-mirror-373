from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.section_object_mode import SectionObjectMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="SectionObject")


@_attrs_define
class SectionObject:
    """
    Attributes:
        start (Union[Unset, float]): The starting point (in seconds) of the section.
        duration (Union[Unset, float]): The duration (in seconds) of the section. Example: 6.97092.
        confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the section's
            "designation". Example: 1.0.
        loudness (Union[Unset, float]): The overall loudness of the section in decibels (dB). Loudness values are useful
            for comparing relative loudness of sections within tracks. Example: -14.938.
        tempo (Union[Unset, float]): The overall estimated tempo of the section in beats per minute (BPM). In musical
            terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
            Example: 113.178.
        tempo_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the tempo. Some
            tracks contain tempo changes or sounds which don't contain tempo (like pure speech) which would correspond to a
            low value in this field. Example: 0.647.
        key (Union[Unset, int]): The estimated overall key of the section. The values in this field ranging from 0 to 11
            mapping to pitches using standard Pitch Class notation (E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on). If no key was
            detected, the value is -1. Example: 9.
        key_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the key. Songs with
            many key changes may correspond to low values in this field. Example: 0.297.
        mode (Union[Unset, SectionObjectMode]): Indicates the modality (major or minor) of a section, the type of scale
            from which its melodic content is derived. This field will contain a 0 for "minor", a 1 for "major", or a -1 for
            no result. Note that the major key (e.g. C major) could more likely be confused with the minor key at 3
            semitones lower (e.g. A minor) as both keys carry the same pitches.
        mode_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the `mode`.
            Example: 0.471.
        time_signature (Union[Unset, int]): An estimated time signature. The time signature (meter) is a notational
            convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7
            indicating time signatures of "3/4", to "7/4". Example: 4.
        time_signature_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the
            `time_signature`. Sections with time signature changes may correspond to low values in this field. Example: 1.0.
    """

    start: Union[Unset, float] = UNSET
    duration: Union[Unset, float] = UNSET
    confidence: Union[Unset, float] = UNSET
    loudness: Union[Unset, float] = UNSET
    tempo: Union[Unset, float] = UNSET
    tempo_confidence: Union[Unset, float] = UNSET
    key: Union[Unset, int] = UNSET
    key_confidence: Union[Unset, float] = UNSET
    mode: Union[Unset, SectionObjectMode] = UNSET
    mode_confidence: Union[Unset, float] = UNSET
    time_signature: Union[Unset, int] = UNSET
    time_signature_confidence: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start = self.start

        duration = self.duration

        confidence = self.confidence

        loudness = self.loudness

        tempo = self.tempo

        tempo_confidence = self.tempo_confidence

        key = self.key

        key_confidence = self.key_confidence

        mode: Union[Unset, int] = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        mode_confidence = self.mode_confidence

        time_signature = self.time_signature

        time_signature_confidence = self.time_signature_confidence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start is not UNSET:
            field_dict["start"] = start
        if duration is not UNSET:
            field_dict["duration"] = duration
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if loudness is not UNSET:
            field_dict["loudness"] = loudness
        if tempo is not UNSET:
            field_dict["tempo"] = tempo
        if tempo_confidence is not UNSET:
            field_dict["tempo_confidence"] = tempo_confidence
        if key is not UNSET:
            field_dict["key"] = key
        if key_confidence is not UNSET:
            field_dict["key_confidence"] = key_confidence
        if mode is not UNSET:
            field_dict["mode"] = mode
        if mode_confidence is not UNSET:
            field_dict["mode_confidence"] = mode_confidence
        if time_signature is not UNSET:
            field_dict["time_signature"] = time_signature
        if time_signature_confidence is not UNSET:
            field_dict["time_signature_confidence"] = time_signature_confidence

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start = d.pop("start", UNSET)

        duration = d.pop("duration", UNSET)

        confidence = d.pop("confidence", UNSET)

        loudness = d.pop("loudness", UNSET)

        tempo = d.pop("tempo", UNSET)

        tempo_confidence = d.pop("tempo_confidence", UNSET)

        key = d.pop("key", UNSET)

        key_confidence = d.pop("key_confidence", UNSET)

        _mode = d.pop("mode", UNSET)
        mode: Union[Unset, SectionObjectMode]
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = SectionObjectMode(_mode)

        mode_confidence = d.pop("mode_confidence", UNSET)

        time_signature = d.pop("time_signature", UNSET)

        time_signature_confidence = d.pop("time_signature_confidence", UNSET)

        section_object = cls(
            start=start,
            duration=duration,
            confidence=confidence,
            loudness=loudness,
            tempo=tempo,
            tempo_confidence=tempo_confidence,
            key=key,
            key_confidence=key_confidence,
            mode=mode,
            mode_confidence=mode_confidence,
            time_signature=time_signature,
            time_signature_confidence=time_signature_confidence,
        )

        section_object.additional_properties = d
        return section_object

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
