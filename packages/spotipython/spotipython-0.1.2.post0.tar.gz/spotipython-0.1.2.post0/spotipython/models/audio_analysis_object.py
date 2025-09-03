from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.audio_analysis_object_meta import AudioAnalysisObjectMeta
    from ..models.audio_analysis_object_track import AudioAnalysisObjectTrack
    from ..models.section_object import SectionObject
    from ..models.segment_object import SegmentObject
    from ..models.time_interval_object import TimeIntervalObject


T = TypeVar("T", bound="AudioAnalysisObject")


@_attrs_define
class AudioAnalysisObject:
    """
    Attributes:
        meta (Union[Unset, AudioAnalysisObjectMeta]):
        track (Union[Unset, AudioAnalysisObjectTrack]):
        bars (Union[Unset, list['TimeIntervalObject']]): The time intervals of the bars throughout the track. A bar (or
            measure) is a segment of time defined as a given number of beats.
        beats (Union[Unset, list['TimeIntervalObject']]): The time intervals of beats throughout the track. A beat is
            the basic time unit of a piece of music; for example, each tick of a metronome. Beats are typically multiples of
            tatums.
        sections (Union[Unset, list['SectionObject']]): Sections are defined by large variations in rhythm or timbre,
            e.g. chorus, verse, bridge, guitar solo, etc. Each section contains its own descriptions of tempo, key, mode,
            time_signature, and loudness.
        segments (Union[Unset, list['SegmentObject']]): Each segment contains a roughly conisistent sound throughout its
            duration.
        tatums (Union[Unset, list['TimeIntervalObject']]): A tatum represents the lowest regular pulse train that a
            listener intuitively infers from the timing of perceived musical events (segments).
    """

    meta: Union[Unset, "AudioAnalysisObjectMeta"] = UNSET
    track: Union[Unset, "AudioAnalysisObjectTrack"] = UNSET
    bars: Union[Unset, list["TimeIntervalObject"]] = UNSET
    beats: Union[Unset, list["TimeIntervalObject"]] = UNSET
    sections: Union[Unset, list["SectionObject"]] = UNSET
    segments: Union[Unset, list["SegmentObject"]] = UNSET
    tatums: Union[Unset, list["TimeIntervalObject"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        meta: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        track: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.track, Unset):
            track = self.track.to_dict()

        bars: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.bars, Unset):
            bars = []
            for bars_item_data in self.bars:
                bars_item = bars_item_data.to_dict()
                bars.append(bars_item)

        beats: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.beats, Unset):
            beats = []
            for beats_item_data in self.beats:
                beats_item = beats_item_data.to_dict()
                beats.append(beats_item)

        sections: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sections, Unset):
            sections = []
            for sections_item_data in self.sections:
                sections_item = sections_item_data.to_dict()
                sections.append(sections_item)

        segments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.segments, Unset):
            segments = []
            for segments_item_data in self.segments:
                segments_item = segments_item_data.to_dict()
                segments.append(segments_item)

        tatums: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tatums, Unset):
            tatums = []
            for tatums_item_data in self.tatums:
                tatums_item = tatums_item_data.to_dict()
                tatums.append(tatums_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if meta is not UNSET:
            field_dict["meta"] = meta
        if track is not UNSET:
            field_dict["track"] = track
        if bars is not UNSET:
            field_dict["bars"] = bars
        if beats is not UNSET:
            field_dict["beats"] = beats
        if sections is not UNSET:
            field_dict["sections"] = sections
        if segments is not UNSET:
            field_dict["segments"] = segments
        if tatums is not UNSET:
            field_dict["tatums"] = tatums

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audio_analysis_object_meta import AudioAnalysisObjectMeta
        from ..models.audio_analysis_object_track import AudioAnalysisObjectTrack
        from ..models.section_object import SectionObject
        from ..models.segment_object import SegmentObject
        from ..models.time_interval_object import TimeIntervalObject

        d = dict(src_dict)
        _meta = d.pop("meta", UNSET)
        meta: Union[Unset, AudioAnalysisObjectMeta]
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = AudioAnalysisObjectMeta.from_dict(_meta)

        _track = d.pop("track", UNSET)
        track: Union[Unset, AudioAnalysisObjectTrack]
        if isinstance(_track, Unset):
            track = UNSET
        else:
            track = AudioAnalysisObjectTrack.from_dict(_track)

        bars = []
        _bars = d.pop("bars", UNSET)
        for bars_item_data in _bars or []:
            bars_item = TimeIntervalObject.from_dict(bars_item_data)

            bars.append(bars_item)

        beats = []
        _beats = d.pop("beats", UNSET)
        for beats_item_data in _beats or []:
            beats_item = TimeIntervalObject.from_dict(beats_item_data)

            beats.append(beats_item)

        sections = []
        _sections = d.pop("sections", UNSET)
        for sections_item_data in _sections or []:
            sections_item = SectionObject.from_dict(sections_item_data)

            sections.append(sections_item)

        segments = []
        _segments = d.pop("segments", UNSET)
        for segments_item_data in _segments or []:
            segments_item = SegmentObject.from_dict(segments_item_data)

            segments.append(segments_item)

        tatums = []
        _tatums = d.pop("tatums", UNSET)
        for tatums_item_data in _tatums or []:
            tatums_item = TimeIntervalObject.from_dict(tatums_item_data)

            tatums.append(tatums_item)

        audio_analysis_object = cls(
            meta=meta,
            track=track,
            bars=bars,
            beats=beats,
            sections=sections,
            segments=segments,
            tatums=tatums,
        )

        audio_analysis_object.additional_properties = d
        return audio_analysis_object

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
