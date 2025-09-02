from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SegmentObject")


@_attrs_define
class SegmentObject:
    """
    Attributes:
        start (Union[Unset, float]): The starting point (in seconds) of the segment. Example: 0.70154.
        duration (Union[Unset, float]): The duration (in seconds) of the segment. Example: 0.19891.
        confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the segmentation.
            Segments of the song which are difficult to logically segment (e.g: noise) may correspond to low values in this
            field.
             Example: 0.435.
        loudness_start (Union[Unset, float]): The onset loudness of the segment in decibels (dB). Combined with
            `loudness_max` and `loudness_max_time`, these components can be used to describe the "attack" of the segment.
            Example: -23.053.
        loudness_max (Union[Unset, float]): The peak loudness of the segment in decibels (dB). Combined with
            `loudness_start` and `loudness_max_time`, these components can be used to describe the "attack" of the segment.
            Example: -14.25.
        loudness_max_time (Union[Unset, float]): The segment-relative offset of the segment peak loudness in seconds.
            Combined with `loudness_start` and `loudness_max`, these components can be used to desctibe the "attack" of the
            segment. Example: 0.07305.
        loudness_end (Union[Unset, float]): The offset loudness of the segment in decibels (dB). This value should be
            equivalent to the loudness_start of the following segment.
        pitches (Union[Unset, list[float]]): Pitch content is given by a “chroma” vector, corresponding to the 12 pitch
            classes C, C#, D to B, with values ranging from 0 to 1 that describe the relative dominance of every pitch in
            the chromatic scale. For example a C Major chord would likely be represented by large values of C, E and G (i.e.
            classes 0, 4, and 7).

            Vectors are normalized to 1 by their strongest dimension, therefore noisy sounds are likely represented by
            values that are all close to 1, while pure tones are described by one value at 1 (the pitch) and others near 0.
            As can be seen below, the 12 vector indices are a combination of low-power spectrum values at their respective
            pitch frequencies.
            ![pitch vector](/assets/audio/Pitch_vector.png)
             Example: [0.212, 0.141, 0.294].
        timbre (Union[Unset, list[float]]): Timbre is the quality of a musical note or sound that distinguishes
            different types of musical instruments, or voices. It is a complex notion also referred to as sound color,
            texture, or tone quality, and is derived from the shape of a segment’s spectro-temporal surface, independently
            of pitch and loudness. The timbre feature is a vector that includes 12 unbounded values roughly centered around
            0. Those values are high level abstractions of the spectral surface, ordered by degree of importance.

            For completeness however, the first dimension represents the average loudness of the segment; second emphasizes
            brightness; third is more closely correlated to the flatness of a sound; fourth to sounds with a stronger
            attack; etc. See an image below representing the 12 basis functions (i.e. template segments).
            ![timbre basis functions](/assets/audio/Timbre_basis_functions.png)

            The actual timbre of the segment is best described as a linear combination of these 12 basis functions weighted
            by the coefficient values: timbre = c1 x b1 + c2 x b2 + ... + c12 x b12, where c1 to c12 represent the 12
            coefficients and b1 to b12 the 12 basis functions as displayed below. Timbre vectors are best used in comparison
            with each other.
             Example: [42.115, 64.373, -0.233].
    """

    start: Union[Unset, float] = UNSET
    duration: Union[Unset, float] = UNSET
    confidence: Union[Unset, float] = UNSET
    loudness_start: Union[Unset, float] = UNSET
    loudness_max: Union[Unset, float] = UNSET
    loudness_max_time: Union[Unset, float] = UNSET
    loudness_end: Union[Unset, float] = UNSET
    pitches: Union[Unset, list[float]] = UNSET
    timbre: Union[Unset, list[float]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start = self.start

        duration = self.duration

        confidence = self.confidence

        loudness_start = self.loudness_start

        loudness_max = self.loudness_max

        loudness_max_time = self.loudness_max_time

        loudness_end = self.loudness_end

        pitches: Union[Unset, list[float]] = UNSET
        if not isinstance(self.pitches, Unset):
            pitches = self.pitches

        timbre: Union[Unset, list[float]] = UNSET
        if not isinstance(self.timbre, Unset):
            timbre = self.timbre

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start is not UNSET:
            field_dict["start"] = start
        if duration is not UNSET:
            field_dict["duration"] = duration
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if loudness_start is not UNSET:
            field_dict["loudness_start"] = loudness_start
        if loudness_max is not UNSET:
            field_dict["loudness_max"] = loudness_max
        if loudness_max_time is not UNSET:
            field_dict["loudness_max_time"] = loudness_max_time
        if loudness_end is not UNSET:
            field_dict["loudness_end"] = loudness_end
        if pitches is not UNSET:
            field_dict["pitches"] = pitches
        if timbre is not UNSET:
            field_dict["timbre"] = timbre

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start = d.pop("start", UNSET)

        duration = d.pop("duration", UNSET)

        confidence = d.pop("confidence", UNSET)

        loudness_start = d.pop("loudness_start", UNSET)

        loudness_max = d.pop("loudness_max", UNSET)

        loudness_max_time = d.pop("loudness_max_time", UNSET)

        loudness_end = d.pop("loudness_end", UNSET)

        pitches = cast(list[float], d.pop("pitches", UNSET))

        timbre = cast(list[float], d.pop("timbre", UNSET))

        segment_object = cls(
            start=start,
            duration=duration,
            confidence=confidence,
            loudness_start=loudness_start,
            loudness_max=loudness_max,
            loudness_max_time=loudness_max_time,
            loudness_end=loudness_end,
            pitches=pitches,
            timbre=timbre,
        )

        segment_object.additional_properties = d
        return segment_object

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
