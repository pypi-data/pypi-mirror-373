from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.audio_features_object_type import AudioFeaturesObjectType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AudioFeaturesObject")


@_attrs_define
class AudioFeaturesObject:
    """
    Attributes:
        acousticness (Union[Unset, float]): A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0
            represents high confidence the track is acoustic.
             Example: 0.00242.
        analysis_url (Union[Unset, str]): A URL to access the full audio analysis of this track. An access token is
            required to access this data.
             Example: https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B
            .
        danceability (Union[Unset, float]): Danceability describes how suitable a track is for dancing based on a
            combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A
            value of 0.0 is least danceable and 1.0 is most danceable.
             Example: 0.585.
        duration_ms (Union[Unset, int]): The duration of the track in milliseconds.
             Example: 237040.
        energy (Union[Unset, float]): Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of
            intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has
            high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute
            include dynamic range, perceived loudness, timbre, onset rate, and general entropy.
             Example: 0.842.
        id (Union[Unset, str]): The Spotify ID for the track.
             Example: 2takcwOaAZWiXQijPHIx7B.
        instrumentalness (Union[Unset, float]): Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are
            treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the
            instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5
            are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.
             Example: 0.00686.
        key (Union[Unset, int]): The key the track is in. Integers map to pitches using standard [Pitch Class
            notation](https://en.wikipedia.org/wiki/Pitch_class). E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was
            detected, the value is -1.
             Example: 9.
        liveness (Union[Unset, float]): Detects the presence of an audience in the recording. Higher liveness values
            represent an increased probability that the track was performed live. A value above 0.8 provides strong
            likelihood that the track is live.
             Example: 0.0866.
        loudness (Union[Unset, float]): The overall loudness of a track in decibels (dB). Loudness values are averaged
            across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a
            sound that is the primary psychological correlate of physical strength (amplitude). Values typically range
            between -60 and 0 db.
             Example: -5.883.
        mode (Union[Unset, int]): Mode indicates the modality (major or minor) of a track, the type of scale from which
            its melodic content is derived. Major is represented by 1 and minor is 0.
        speechiness (Union[Unset, float]): Speechiness detects the presence of spoken words in a track. The more
            exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute
            value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33
            and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such
            cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.
             Example: 0.0556.
        tempo (Union[Unset, float]): The overall estimated tempo of a track in beats per minute (BPM). In musical
            terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
             Example: 118.211.
        time_signature (Union[Unset, int]): An estimated time signature. The time signature (meter) is a notational
            convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7
            indicating time signatures of "3/4", to "7/4". Example: 4.
        track_href (Union[Unset, str]): A link to the Web API endpoint providing full details of the track.
             Example: https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B
            .
        type_ (Union[Unset, AudioFeaturesObjectType]): The object type.
        uri (Union[Unset, str]): The Spotify URI for the track.
             Example: spotify:track:2takcwOaAZWiXQijPHIx7B.
        valence (Union[Unset, float]): A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a
            track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low
            valence sound more negative (e.g. sad, depressed, angry).
             Example: 0.428.
    """

    acousticness: Union[Unset, float] = UNSET
    analysis_url: Union[Unset, str] = UNSET
    danceability: Union[Unset, float] = UNSET
    duration_ms: Union[Unset, int] = UNSET
    energy: Union[Unset, float] = UNSET
    id: Union[Unset, str] = UNSET
    instrumentalness: Union[Unset, float] = UNSET
    key: Union[Unset, int] = UNSET
    liveness: Union[Unset, float] = UNSET
    loudness: Union[Unset, float] = UNSET
    mode: Union[Unset, int] = UNSET
    speechiness: Union[Unset, float] = UNSET
    tempo: Union[Unset, float] = UNSET
    time_signature: Union[Unset, int] = UNSET
    track_href: Union[Unset, str] = UNSET
    type_: Union[Unset, AudioFeaturesObjectType] = UNSET
    uri: Union[Unset, str] = UNSET
    valence: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        acousticness = self.acousticness

        analysis_url = self.analysis_url

        danceability = self.danceability

        duration_ms = self.duration_ms

        energy = self.energy

        id = self.id

        instrumentalness = self.instrumentalness

        key = self.key

        liveness = self.liveness

        loudness = self.loudness

        mode = self.mode

        speechiness = self.speechiness

        tempo = self.tempo

        time_signature = self.time_signature

        track_href = self.track_href

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        uri = self.uri

        valence = self.valence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if acousticness is not UNSET:
            field_dict["acousticness"] = acousticness
        if analysis_url is not UNSET:
            field_dict["analysis_url"] = analysis_url
        if danceability is not UNSET:
            field_dict["danceability"] = danceability
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if energy is not UNSET:
            field_dict["energy"] = energy
        if id is not UNSET:
            field_dict["id"] = id
        if instrumentalness is not UNSET:
            field_dict["instrumentalness"] = instrumentalness
        if key is not UNSET:
            field_dict["key"] = key
        if liveness is not UNSET:
            field_dict["liveness"] = liveness
        if loudness is not UNSET:
            field_dict["loudness"] = loudness
        if mode is not UNSET:
            field_dict["mode"] = mode
        if speechiness is not UNSET:
            field_dict["speechiness"] = speechiness
        if tempo is not UNSET:
            field_dict["tempo"] = tempo
        if time_signature is not UNSET:
            field_dict["time_signature"] = time_signature
        if track_href is not UNSET:
            field_dict["track_href"] = track_href
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uri is not UNSET:
            field_dict["uri"] = uri
        if valence is not UNSET:
            field_dict["valence"] = valence

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        acousticness = d.pop("acousticness", UNSET)

        analysis_url = d.pop("analysis_url", UNSET)

        danceability = d.pop("danceability", UNSET)

        duration_ms = d.pop("duration_ms", UNSET)

        energy = d.pop("energy", UNSET)

        id = d.pop("id", UNSET)

        instrumentalness = d.pop("instrumentalness", UNSET)

        key = d.pop("key", UNSET)

        liveness = d.pop("liveness", UNSET)

        loudness = d.pop("loudness", UNSET)

        mode = d.pop("mode", UNSET)

        speechiness = d.pop("speechiness", UNSET)

        tempo = d.pop("tempo", UNSET)

        time_signature = d.pop("time_signature", UNSET)

        track_href = d.pop("track_href", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, AudioFeaturesObjectType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = AudioFeaturesObjectType(_type_)

        uri = d.pop("uri", UNSET)

        valence = d.pop("valence", UNSET)

        audio_features_object = cls(
            acousticness=acousticness,
            analysis_url=analysis_url,
            danceability=danceability,
            duration_ms=duration_ms,
            energy=energy,
            id=id,
            instrumentalness=instrumentalness,
            key=key,
            liveness=liveness,
            loudness=loudness,
            mode=mode,
            speechiness=speechiness,
            tempo=tempo,
            time_signature=time_signature,
            track_href=track_href,
            type_=type_,
            uri=uri,
            valence=valence,
        )

        audio_features_object.additional_properties = d
        return audio_features_object

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
