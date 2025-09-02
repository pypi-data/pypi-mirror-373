from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AudioAnalysisObjectMeta")


@_attrs_define
class AudioAnalysisObjectMeta:
    """
    Attributes:
        analysis_time (Union[Unset, float]): The amount of time taken to analyze this track. Example: 6.93906.
        analyzer_version (Union[Unset, str]): The version of the Analyzer used to analyze this track. Example: 4.0.0.
        detailed_status (Union[Unset, str]): A detailed status code for this track. If analysis data is missing, this
            code may explain why. Example: OK.
        input_process (Union[Unset, str]): The method used to read the track's audio data. Example: libvorbisfile L+R
            44100->22050.
        platform (Union[Unset, str]): The platform used to read the track's audio data. Example: Linux.
        status_code (Union[Unset, int]): The return code of the analyzer process. 0 if successful, 1 if any errors
            occurred.
        timestamp (Union[Unset, int]): The Unix timestamp (in seconds) at which this track was analyzed. Example:
            1495193577.
    """

    analysis_time: Union[Unset, float] = UNSET
    analyzer_version: Union[Unset, str] = UNSET
    detailed_status: Union[Unset, str] = UNSET
    input_process: Union[Unset, str] = UNSET
    platform: Union[Unset, str] = UNSET
    status_code: Union[Unset, int] = UNSET
    timestamp: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        analysis_time = self.analysis_time

        analyzer_version = self.analyzer_version

        detailed_status = self.detailed_status

        input_process = self.input_process

        platform = self.platform

        status_code = self.status_code

        timestamp = self.timestamp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if analysis_time is not UNSET:
            field_dict["analysis_time"] = analysis_time
        if analyzer_version is not UNSET:
            field_dict["analyzer_version"] = analyzer_version
        if detailed_status is not UNSET:
            field_dict["detailed_status"] = detailed_status
        if input_process is not UNSET:
            field_dict["input_process"] = input_process
        if platform is not UNSET:
            field_dict["platform"] = platform
        if status_code is not UNSET:
            field_dict["status_code"] = status_code
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        analysis_time = d.pop("analysis_time", UNSET)

        analyzer_version = d.pop("analyzer_version", UNSET)

        detailed_status = d.pop("detailed_status", UNSET)

        input_process = d.pop("input_process", UNSET)

        platform = d.pop("platform", UNSET)

        status_code = d.pop("status_code", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        audio_analysis_object_meta = cls(
            analysis_time=analysis_time,
            analyzer_version=analyzer_version,
            detailed_status=detailed_status,
            input_process=input_process,
            platform=platform,
            status_code=status_code,
            timestamp=timestamp,
        )

        audio_analysis_object_meta.additional_properties = d
        return audio_analysis_object_meta

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
