from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.episode_base_release_date_precision import EpisodeBaseReleaseDatePrecision
from ..models.episode_base_type import EpisodeBaseType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.episode_restriction_object import EpisodeRestrictionObject
    from ..models.external_url_object import ExternalUrlObject
    from ..models.image_object import ImageObject
    from ..models.resume_point_object import ResumePointObject


T = TypeVar("T", bound="SimplifiedEpisodeObject")


@_attrs_define
class SimplifiedEpisodeObject:
    """
    Attributes:
        audio_preview_url (Union[None, str]): A URL to a 30 second preview (MP3 format) of the episode. `null` if not
            available.
             Example: https://p.scdn.co/mp3-preview/2f37da1d4221f40b9d1a98cd191f4d6f1646ad17.
        description (str): A description of the episode. HTML tags are stripped away from this field, use
            `html_description` field in case HTML tags are needed.
             Example: A Spotify podcast sharing fresh insights on important topics of the moment—in a way only Spotify can.
            You’ll hear from experts in the music, podcast and tech industries as we discover and uncover stories about our
            work and the world around us.
            .
        html_description (str): A description of the episode. This field may contain HTML tags.
             Example: <p>A Spotify podcast sharing fresh insights on important topics of the moment—in a way only Spotify
            can. You’ll hear from experts in the music, podcast and tech industries as we discover and uncover stories about
            our work and the world around us.</p>
            .
        duration_ms (int): The episode length in milliseconds.
             Example: 1686230.
        explicit (bool): Whether or not the episode has explicit content (true = yes it does; false = no it does not OR
            unknown).
        external_urls (ExternalUrlObject):
        href (str): A link to the Web API endpoint providing full details of the episode.
             Example: https://api.spotify.com/v1/episodes/5Xt5DXGzch68nYYamXrNxZ.
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the episode.
             Example: 5Xt5DXGzch68nYYamXrNxZ.
        images (list['ImageObject']): The cover art for the episode in various sizes, widest first.
        is_externally_hosted (bool): True if the episode is hosted outside of Spotify's CDN.
        is_playable (bool): True if the episode is playable in the given market. Otherwise false.
        languages (list[str]): A list of the languages used in the episode, identified by their [ISO
            639-1](https://en.wikipedia.org/wiki/ISO_639) code.
             Example: ['fr', 'en'].
        name (str): The name of the episode.
             Example: Starting Your Own Podcast: Tips, Tricks, and Advice From Anchor Creators
            .
        release_date (str): The date the episode was first released, for example `"1981-12-15"`. Depending on the
            precision, it might be shown as `"1981"` or `"1981-12"`.
             Example: 1981-12-15.
        release_date_precision (EpisodeBaseReleaseDatePrecision): The precision with which `release_date` value is
            known.
             Example: day.
        type_ (EpisodeBaseType): The object type.
        uri (str): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the episode.
             Example: spotify:episode:0zLhl3WsOCQHbe1BPTiHgr.
        language (Union[Unset, str]): The language used in the episode, identified by a [ISO
            639](https://en.wikipedia.org/wiki/ISO_639) code. This field is deprecated and might be removed in the future.
            Please use the `languages` field instead.
             Example: en.
        resume_point (Union[Unset, ResumePointObject]):
        restrictions (Union[Unset, EpisodeRestrictionObject]):
    """

    audio_preview_url: Union[None, str]
    description: str
    html_description: str
    duration_ms: int
    explicit: bool
    external_urls: "ExternalUrlObject"
    href: str
    id: str
    images: list["ImageObject"]
    is_externally_hosted: bool
    is_playable: bool
    languages: list[str]
    name: str
    release_date: str
    release_date_precision: EpisodeBaseReleaseDatePrecision
    type_: EpisodeBaseType
    uri: str
    language: Union[Unset, str] = UNSET
    resume_point: Union[Unset, "ResumePointObject"] = UNSET
    restrictions: Union[Unset, "EpisodeRestrictionObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audio_preview_url: Union[None, str]
        audio_preview_url = self.audio_preview_url

        description = self.description

        html_description = self.html_description

        duration_ms = self.duration_ms

        explicit = self.explicit

        external_urls = self.external_urls.to_dict()

        href = self.href

        id = self.id

        images = []
        for images_item_data in self.images:
            images_item = images_item_data.to_dict()
            images.append(images_item)

        is_externally_hosted = self.is_externally_hosted

        is_playable = self.is_playable

        languages = self.languages

        name = self.name

        release_date = self.release_date

        release_date_precision = self.release_date_precision.value

        type_ = self.type_.value

        uri = self.uri

        language = self.language

        resume_point: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.resume_point, Unset):
            resume_point = self.resume_point.to_dict()

        restrictions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.restrictions, Unset):
            restrictions = self.restrictions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "audio_preview_url": audio_preview_url,
                "description": description,
                "html_description": html_description,
                "duration_ms": duration_ms,
                "explicit": explicit,
                "external_urls": external_urls,
                "href": href,
                "id": id,
                "images": images,
                "is_externally_hosted": is_externally_hosted,
                "is_playable": is_playable,
                "languages": languages,
                "name": name,
                "release_date": release_date,
                "release_date_precision": release_date_precision,
                "type": type_,
                "uri": uri,
            }
        )
        if language is not UNSET:
            field_dict["language"] = language
        if resume_point is not UNSET:
            field_dict["resume_point"] = resume_point
        if restrictions is not UNSET:
            field_dict["restrictions"] = restrictions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.episode_restriction_object import EpisodeRestrictionObject
        from ..models.external_url_object import ExternalUrlObject
        from ..models.image_object import ImageObject
        from ..models.resume_point_object import ResumePointObject

        d = dict(src_dict)

        def _parse_audio_preview_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        audio_preview_url = _parse_audio_preview_url(d.pop("audio_preview_url"))

        description = d.pop("description")

        html_description = d.pop("html_description")

        duration_ms = d.pop("duration_ms")

        explicit = d.pop("explicit")

        external_urls = ExternalUrlObject.from_dict(d.pop("external_urls"))

        href = d.pop("href")

        id = d.pop("id")

        images = []
        _images = d.pop("images")
        for images_item_data in _images:
            images_item = ImageObject.from_dict(images_item_data)

            images.append(images_item)

        is_externally_hosted = d.pop("is_externally_hosted")

        is_playable = d.pop("is_playable")

        languages = cast(list[str], d.pop("languages"))

        name = d.pop("name")

        release_date = d.pop("release_date")

        release_date_precision = EpisodeBaseReleaseDatePrecision(d.pop("release_date_precision"))

        type_ = EpisodeBaseType(d.pop("type"))

        uri = d.pop("uri")

        language = d.pop("language", UNSET)

        _resume_point = d.pop("resume_point", UNSET)
        resume_point: Union[Unset, ResumePointObject]
        if isinstance(_resume_point, Unset):
            resume_point = UNSET
        else:
            resume_point = ResumePointObject.from_dict(_resume_point)

        _restrictions = d.pop("restrictions", UNSET)
        restrictions: Union[Unset, EpisodeRestrictionObject]
        if isinstance(_restrictions, Unset):
            restrictions = UNSET
        else:
            restrictions = EpisodeRestrictionObject.from_dict(_restrictions)

        simplified_episode_object = cls(
            audio_preview_url=audio_preview_url,
            description=description,
            html_description=html_description,
            duration_ms=duration_ms,
            explicit=explicit,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            is_externally_hosted=is_externally_hosted,
            is_playable=is_playable,
            languages=languages,
            name=name,
            release_date=release_date,
            release_date_precision=release_date_precision,
            type_=type_,
            uri=uri,
            language=language,
            resume_point=resume_point,
            restrictions=restrictions,
        )

        simplified_episode_object.additional_properties = d
        return simplified_episode_object

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
