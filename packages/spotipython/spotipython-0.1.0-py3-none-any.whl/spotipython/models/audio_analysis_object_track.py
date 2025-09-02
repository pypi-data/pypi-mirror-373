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
        analysis_channels (Union[Unset, int]): The number of channels used for analysis. If 1, all channels are summed
            together to mono before analysis. Example: 1.
        analysis_sample_rate (Union[Unset, int]): The sample rate used to decode and analyze this track. May differ from
            the actual sample rate of this track available on Spotify. Example: 22050.
        code_version (Union[Unset, float]): A version number for the Echo Nest Musical Fingerprint format used in the
            codestring field. Example: 3.15.
        codestring (Union[Unset, str]): An [Echo Nest Musical Fingerprint
            (ENMFP)](https://academiccommons.columbia.edu/doi/10.7916/D8Q248M4) codestring for this track.
        duration (Union[Unset, float]): Length of the track in seconds. Example: 207.95985.
        echoprint_version (Union[Unset, float]): A version number for the EchoPrint format used in the echoprintstring
            field. Example: 4.15.
        echoprintstring (Union[Unset, str]): An [EchoPrint](https://github.com/spotify/echoprint-codegen) codestring for
            this track.
        end_of_fade_in (Union[Unset, float]): The time, in seconds, at which the track's fade-in period ends. If the
            track has no fade-in, this will be 0.0.
        key (Union[Unset, int]): The key the track is in. Integers map to pitches using standard [Pitch Class
            notation](https://en.wikipedia.org/wiki/Pitch_class). E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was
            detected, the value is -1.
             Example: 9.
        key_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the `key`. Example:
            0.408.
        loudness (Union[Unset, float]): The overall loudness of a track in decibels (dB). Loudness values are averaged
            across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a
            sound that is the primary psychological correlate of physical strength (amplitude). Values typically range
            between -60 and 0 db.
             Example: -5.883.
        mode (Union[Unset, int]): Mode indicates the modality (major or minor) of a track, the type of scale from which
            its melodic content is derived. Major is represented by 1 and minor is 0.
        mode_confidence (Union[Unset, float]): The confidence, from 0.0 to 1.0, of the reliability of the `mode`.
            Example: 0.485.
        num_samples (Union[Unset, int]): The exact number of audio samples analyzed from this track. See also
            `analysis_sample_rate`. Example: 4585515.
        offset_seconds (Union[Unset, int]): An offset to the start of the region of the track that was analyzed. (As the
            entire track is analyzed, this should always be 0.)
        rhythm_version (Union[Unset, float]): A version number for the Rhythmstring used in the rhythmstring field.
            Example: 1.
        rhythmstring (Union[Unset, str]): A Rhythmstring for this track. The format of this string is similar to the
            Synchstring.
        sample_md5 (Union[Unset, str]): This field will always contain the empty string.
        start_of_fade_out (Union[Unset, float]): The time, in seconds, at which the track's fade-out period starts. If
            the track has no fade-out, this should match the track's length. Example: 201.13705.
        synch_version (Union[Unset, float]): A version number for the Synchstring used in the synchstring field.
            Example: 1.
        synchstring (Union[Unset, str]): A [Synchstring](https://github.com/echonest/synchdata) for this track.
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
        window_seconds (Union[Unset, int]): The length of the region of the track was analyzed, if a subset of the track
            was analyzed. (As the entire track is analyzed, this should always be 0.)
    """

    analysis_channels: Union[Unset, int] = UNSET
    analysis_sample_rate: Union[Unset, int] = UNSET
    code_version: Union[Unset, float] = UNSET
    codestring: Union[Unset, str] = UNSET
    duration: Union[Unset, float] = UNSET
    echoprint_version: Union[Unset, float] = UNSET
    echoprintstring: Union[Unset, str] = UNSET
    end_of_fade_in: Union[Unset, float] = UNSET
    key: Union[Unset, int] = UNSET
    key_confidence: Union[Unset, float] = UNSET
    loudness: Union[Unset, float] = UNSET
    mode: Union[Unset, int] = UNSET
    mode_confidence: Union[Unset, float] = UNSET
    num_samples: Union[Unset, int] = UNSET
    offset_seconds: Union[Unset, int] = UNSET
    rhythm_version: Union[Unset, float] = UNSET
    rhythmstring: Union[Unset, str] = UNSET
    sample_md5: Union[Unset, str] = UNSET
    start_of_fade_out: Union[Unset, float] = UNSET
    synch_version: Union[Unset, float] = UNSET
    synchstring: Union[Unset, str] = UNSET
    tempo: Union[Unset, float] = UNSET
    tempo_confidence: Union[Unset, float] = UNSET
    time_signature: Union[Unset, int] = UNSET
    time_signature_confidence: Union[Unset, float] = UNSET
    window_seconds: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        analysis_channels = self.analysis_channels

        analysis_sample_rate = self.analysis_sample_rate

        code_version = self.code_version

        codestring = self.codestring

        duration = self.duration

        echoprint_version = self.echoprint_version

        echoprintstring = self.echoprintstring

        end_of_fade_in = self.end_of_fade_in

        key = self.key

        key_confidence = self.key_confidence

        loudness = self.loudness

        mode = self.mode

        mode_confidence = self.mode_confidence

        num_samples = self.num_samples

        offset_seconds = self.offset_seconds

        rhythm_version = self.rhythm_version

        rhythmstring = self.rhythmstring

        sample_md5 = self.sample_md5

        start_of_fade_out = self.start_of_fade_out

        synch_version = self.synch_version

        synchstring = self.synchstring

        tempo = self.tempo

        tempo_confidence = self.tempo_confidence

        time_signature = self.time_signature

        time_signature_confidence = self.time_signature_confidence

        window_seconds = self.window_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if analysis_channels is not UNSET:
            field_dict["analysis_channels"] = analysis_channels
        if analysis_sample_rate is not UNSET:
            field_dict["analysis_sample_rate"] = analysis_sample_rate
        if code_version is not UNSET:
            field_dict["code_version"] = code_version
        if codestring is not UNSET:
            field_dict["codestring"] = codestring
        if duration is not UNSET:
            field_dict["duration"] = duration
        if echoprint_version is not UNSET:
            field_dict["echoprint_version"] = echoprint_version
        if echoprintstring is not UNSET:
            field_dict["echoprintstring"] = echoprintstring
        if end_of_fade_in is not UNSET:
            field_dict["end_of_fade_in"] = end_of_fade_in
        if key is not UNSET:
            field_dict["key"] = key
        if key_confidence is not UNSET:
            field_dict["key_confidence"] = key_confidence
        if loudness is not UNSET:
            field_dict["loudness"] = loudness
        if mode is not UNSET:
            field_dict["mode"] = mode
        if mode_confidence is not UNSET:
            field_dict["mode_confidence"] = mode_confidence
        if num_samples is not UNSET:
            field_dict["num_samples"] = num_samples
        if offset_seconds is not UNSET:
            field_dict["offset_seconds"] = offset_seconds
        if rhythm_version is not UNSET:
            field_dict["rhythm_version"] = rhythm_version
        if rhythmstring is not UNSET:
            field_dict["rhythmstring"] = rhythmstring
        if sample_md5 is not UNSET:
            field_dict["sample_md5"] = sample_md5
        if start_of_fade_out is not UNSET:
            field_dict["start_of_fade_out"] = start_of_fade_out
        if synch_version is not UNSET:
            field_dict["synch_version"] = synch_version
        if synchstring is not UNSET:
            field_dict["synchstring"] = synchstring
        if tempo is not UNSET:
            field_dict["tempo"] = tempo
        if tempo_confidence is not UNSET:
            field_dict["tempo_confidence"] = tempo_confidence
        if time_signature is not UNSET:
            field_dict["time_signature"] = time_signature
        if time_signature_confidence is not UNSET:
            field_dict["time_signature_confidence"] = time_signature_confidence
        if window_seconds is not UNSET:
            field_dict["window_seconds"] = window_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        analysis_channels = d.pop("analysis_channels", UNSET)

        analysis_sample_rate = d.pop("analysis_sample_rate", UNSET)

        code_version = d.pop("code_version", UNSET)

        codestring = d.pop("codestring", UNSET)

        duration = d.pop("duration", UNSET)

        echoprint_version = d.pop("echoprint_version", UNSET)

        echoprintstring = d.pop("echoprintstring", UNSET)

        end_of_fade_in = d.pop("end_of_fade_in", UNSET)

        key = d.pop("key", UNSET)

        key_confidence = d.pop("key_confidence", UNSET)

        loudness = d.pop("loudness", UNSET)

        mode = d.pop("mode", UNSET)

        mode_confidence = d.pop("mode_confidence", UNSET)

        num_samples = d.pop("num_samples", UNSET)

        offset_seconds = d.pop("offset_seconds", UNSET)

        rhythm_version = d.pop("rhythm_version", UNSET)

        rhythmstring = d.pop("rhythmstring", UNSET)

        sample_md5 = d.pop("sample_md5", UNSET)

        start_of_fade_out = d.pop("start_of_fade_out", UNSET)

        synch_version = d.pop("synch_version", UNSET)

        synchstring = d.pop("synchstring", UNSET)

        tempo = d.pop("tempo", UNSET)

        tempo_confidence = d.pop("tempo_confidence", UNSET)

        time_signature = d.pop("time_signature", UNSET)

        time_signature_confidence = d.pop("time_signature_confidence", UNSET)

        window_seconds = d.pop("window_seconds", UNSET)

        audio_analysis_object_track = cls(
            analysis_channels=analysis_channels,
            analysis_sample_rate=analysis_sample_rate,
            code_version=code_version,
            codestring=codestring,
            duration=duration,
            echoprint_version=echoprint_version,
            echoprintstring=echoprintstring,
            end_of_fade_in=end_of_fade_in,
            key=key,
            key_confidence=key_confidence,
            loudness=loudness,
            mode=mode,
            mode_confidence=mode_confidence,
            num_samples=num_samples,
            offset_seconds=offset_seconds,
            rhythm_version=rhythm_version,
            rhythmstring=rhythmstring,
            sample_md5=sample_md5,
            start_of_fade_out=start_of_fade_out,
            synch_version=synch_version,
            synchstring=synchstring,
            tempo=tempo,
            tempo_confidence=tempo_confidence,
            time_signature=time_signature,
            time_signature_confidence=time_signature_confidence,
            window_seconds=window_seconds,
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
