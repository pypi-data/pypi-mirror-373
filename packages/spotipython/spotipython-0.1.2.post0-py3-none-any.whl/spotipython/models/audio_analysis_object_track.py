from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AudioAnalysisObjectTrack")


@_attrs_define
class AudioAnalysisObjectTrack:
    """
    Attributes:
        num_samples (Union[Unset, int]): The exact number of audio samples analyzed from this track. See also
            `analysis_sample_rate`. Example: 4585515.
        duration (Union[Unset, float]): Length of the track in seconds. Example: 207.95985.
        sample_md5 (Union[Unset, str]): This field will always contain the empty string.
        offset_seconds (Union[Unset, int]): An offset to the start of the region of the track that was analyzed. (As the
            entire track is analyzed, this should always be 0.)
        window_seconds (Union[Unset, int]): The length of the region of the track was analyzed, if a subset of the track
            was analyzed. (As the entire track is analyzed, this should always be 0.)
        analysis_sample_rate (Union[Unset, int]): The sample rate used to decode and analyze this track. May differ from
            the actual sample rate of this track available on Spotify. Example: 22050.
        analysis_channels (Union[Unset, int]): The number of channels used for analysis. If 1, all channels are summed
            together to mono before analysis. Example: 1.
        end_of_fade_in (Union[Unset, float]): The time, in seconds, at which the track's fade-in period ends. If the
            track has no fade-in, this will be 0.0.
        start_of_fade_out (Union[Unset, float]): The time, in seconds, at which the track's fade-out period starts. If
            the track has no fade-out, this should match the track's length. Example: 201.13705.
        loudness (Union[Unset, float]): The overall loudness of a track in decibels (dB). Loudness values are averaged
            across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a
            sound that is the primary psychological correlate of physical strength (amplitude). Values typically range
            between -60 and 0 db.
             Example: -5.883.
        tempo (Union[Unset, float]): The overall estimated tempo of a track in beats per minute (BPM). In musical
            terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
             Example: 118.211.
        tempo_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the `tempo`.
            Example: 0.73.
        time_signature (Union[Unset, int]): An estimated time signature. The time signature (meter) is a notational
            convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7
            indicating time signatures of "3/4", to "7/4". Example: 4.
        time_signature_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the
            `time_signature`. Example: 0.994.
        key (Union[Unset, int]): The key the track is in. Integers map to pitches using standard [Pitch Class
            notation](https://en.wikipedia.org/wiki/Pitch_class). E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was
            detected, the value is -1.
             Example: 9.
        key_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the `key`. Example:
            0.408.
        mode (Union[Unset, int]): Mode indicates the modality (major or minor) of a track, the type of scale from which
            its melodic content is derived. Major is represented by 1 and minor is 0.
        mode_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the `mode`.
            Example: 0.485.
        codestring (Union[Unset, str]): An [Echo Nest Musical Fingerprint
            (ENMFP)](https://academiccommons.columbia.edu/doi/10.7916/D8Q248M4) codestring for this track.
        code_version (Union[Unset, float]): A version number for the Echo Nest Musical Fingerprint format used in the
            codestring field. Example: 3.15.
        echoprintstring (Union[Unset, str]): An [EchoPrint](https://github.com/spotify/echoprint-codegen) codestring for
            this track.
        echoprint_version (Union[Unset, float]): A version number for the EchoPrint format used in the echoprintstring
            field. Example: 4.15.
        synchstring (Union[Unset, str]): A [Synchstring](https://github.com/echonest/synchdata) for this track.
        synch_version (Union[Unset, float]): A version number for the Synchstring used in the synchstring field.
            Example: 1.0.
        rhythmstring (Union[Unset, str]): A Rhythmstring for this track. The format of this string is similar to the
            Synchstring.
        rhythm_version (Union[Unset, float]): A version number for the Rhythmstring used in the rhythmstring field.
            Example: 1.0.
    """

    num_samples: Union[Unset, int] = UNSET
    duration: Union[Unset, float] = UNSET
    sample_md5: Union[Unset, str] = UNSET
    offset_seconds: Union[Unset, int] = UNSET
    window_seconds: Union[Unset, int] = UNSET
    analysis_sample_rate: Union[Unset, int] = UNSET
    analysis_channels: Union[Unset, int] = UNSET
    end_of_fade_in: Union[Unset, float] = UNSET
    start_of_fade_out: Union[Unset, float] = UNSET
    loudness: Union[Unset, float] = UNSET
    tempo: Union[Unset, float] = UNSET
    tempo_confidence: Union[Unset, float] = UNSET
    time_signature: Union[Unset, int] = UNSET
    time_signature_confidence: Union[Unset, float] = UNSET
    key: Union[Unset, int] = UNSET
    key_confidence: Union[Unset, float] = UNSET
    mode: Union[Unset, int] = UNSET
    mode_confidence: Union[Unset, float] = UNSET
    codestring: Union[Unset, str] = UNSET
    code_version: Union[Unset, float] = UNSET
    echoprintstring: Union[Unset, str] = UNSET
    echoprint_version: Union[Unset, float] = UNSET
    synchstring: Union[Unset, str] = UNSET
    synch_version: Union[Unset, float] = UNSET
    rhythmstring: Union[Unset, str] = UNSET
    rhythm_version: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        num_samples = self.num_samples

        duration = self.duration

        sample_md5 = self.sample_md5

        offset_seconds = self.offset_seconds

        window_seconds = self.window_seconds

        analysis_sample_rate = self.analysis_sample_rate

        analysis_channels = self.analysis_channels

        end_of_fade_in = self.end_of_fade_in

        start_of_fade_out = self.start_of_fade_out

        loudness = self.loudness

        tempo = self.tempo

        tempo_confidence = self.tempo_confidence

        time_signature = self.time_signature

        time_signature_confidence = self.time_signature_confidence

        key = self.key

        key_confidence = self.key_confidence

        mode = self.mode

        mode_confidence = self.mode_confidence

        codestring = self.codestring

        code_version = self.code_version

        echoprintstring = self.echoprintstring

        echoprint_version = self.echoprint_version

        synchstring = self.synchstring

        synch_version = self.synch_version

        rhythmstring = self.rhythmstring

        rhythm_version = self.rhythm_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if num_samples is not UNSET:
            field_dict["num_samples"] = num_samples
        if duration is not UNSET:
            field_dict["duration"] = duration
        if sample_md5 is not UNSET:
            field_dict["sample_md5"] = sample_md5
        if offset_seconds is not UNSET:
            field_dict["offset_seconds"] = offset_seconds
        if window_seconds is not UNSET:
            field_dict["window_seconds"] = window_seconds
        if analysis_sample_rate is not UNSET:
            field_dict["analysis_sample_rate"] = analysis_sample_rate
        if analysis_channels is not UNSET:
            field_dict["analysis_channels"] = analysis_channels
        if end_of_fade_in is not UNSET:
            field_dict["end_of_fade_in"] = end_of_fade_in
        if start_of_fade_out is not UNSET:
            field_dict["start_of_fade_out"] = start_of_fade_out
        if loudness is not UNSET:
            field_dict["loudness"] = loudness
        if tempo is not UNSET:
            field_dict["tempo"] = tempo
        if tempo_confidence is not UNSET:
            field_dict["tempo_confidence"] = tempo_confidence
        if time_signature is not UNSET:
            field_dict["time_signature"] = time_signature
        if time_signature_confidence is not UNSET:
            field_dict["time_signature_confidence"] = time_signature_confidence
        if key is not UNSET:
            field_dict["key"] = key
        if key_confidence is not UNSET:
            field_dict["key_confidence"] = key_confidence
        if mode is not UNSET:
            field_dict["mode"] = mode
        if mode_confidence is not UNSET:
            field_dict["mode_confidence"] = mode_confidence
        if codestring is not UNSET:
            field_dict["codestring"] = codestring
        if code_version is not UNSET:
            field_dict["code_version"] = code_version
        if echoprintstring is not UNSET:
            field_dict["echoprintstring"] = echoprintstring
        if echoprint_version is not UNSET:
            field_dict["echoprint_version"] = echoprint_version
        if synchstring is not UNSET:
            field_dict["synchstring"] = synchstring
        if synch_version is not UNSET:
            field_dict["synch_version"] = synch_version
        if rhythmstring is not UNSET:
            field_dict["rhythmstring"] = rhythmstring
        if rhythm_version is not UNSET:
            field_dict["rhythm_version"] = rhythm_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        num_samples = d.pop("num_samples", UNSET)

        duration = d.pop("duration", UNSET)

        sample_md5 = d.pop("sample_md5", UNSET)

        offset_seconds = d.pop("offset_seconds", UNSET)

        window_seconds = d.pop("window_seconds", UNSET)

        analysis_sample_rate = d.pop("analysis_sample_rate", UNSET)

        analysis_channels = d.pop("analysis_channels", UNSET)

        end_of_fade_in = d.pop("end_of_fade_in", UNSET)

        start_of_fade_out = d.pop("start_of_fade_out", UNSET)

        loudness = d.pop("loudness", UNSET)

        tempo = d.pop("tempo", UNSET)

        tempo_confidence = d.pop("tempo_confidence", UNSET)

        time_signature = d.pop("time_signature", UNSET)

        time_signature_confidence = d.pop("time_signature_confidence", UNSET)

        key = d.pop("key", UNSET)

        key_confidence = d.pop("key_confidence", UNSET)

        mode = d.pop("mode", UNSET)

        mode_confidence = d.pop("mode_confidence", UNSET)

        codestring = d.pop("codestring", UNSET)

        code_version = d.pop("code_version", UNSET)

        echoprintstring = d.pop("echoprintstring", UNSET)

        echoprint_version = d.pop("echoprint_version", UNSET)

        synchstring = d.pop("synchstring", UNSET)

        synch_version = d.pop("synch_version", UNSET)

        rhythmstring = d.pop("rhythmstring", UNSET)

        rhythm_version = d.pop("rhythm_version", UNSET)

        audio_analysis_object_track = cls(
            num_samples=num_samples,
            duration=duration,
            sample_md5=sample_md5,
            offset_seconds=offset_seconds,
            window_seconds=window_seconds,
            analysis_sample_rate=analysis_sample_rate,
            analysis_channels=analysis_channels,
            end_of_fade_in=end_of_fade_in,
            start_of_fade_out=start_of_fade_out,
            loudness=loudness,
            tempo=tempo,
            tempo_confidence=tempo_confidence,
            time_signature=time_signature,
            time_signature_confidence=time_signature_confidence,
            key=key,
            key_confidence=key_confidence,
            mode=mode,
            mode_confidence=mode_confidence,
            codestring=codestring,
            code_version=code_version,
            echoprintstring=echoprintstring,
            echoprint_version=echoprint_version,
            synchstring=synchstring,
            synch_version=synch_version,
            rhythmstring=rhythmstring,
            rhythm_version=rhythm_version,
        )

        audio_analysis_object_track.additional_properties = d
        return audio_analysis_object_track

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
