from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chapter_base_release_date_precision import ChapterBaseReleaseDatePrecision
from ..models.chapter_base_type import ChapterBaseType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chapter_restriction_object import ChapterRestrictionObject
    from ..models.external_url_object import ExternalUrlObject
    from ..models.image_object import ImageObject
    from ..models.resume_point_object import ResumePointObject


T = TypeVar("T", bound="SimplifiedChapterObject")


@_attrs_define
class SimplifiedChapterObject:
    """
    Attributes:
        audio_preview_url (Union[None, str]): A URL to a 30 second preview (MP3 format) of the chapter. `null` if not
            available.
             Example: https://p.scdn.co/mp3-preview/2f37da1d4221f40b9d1a98cd191f4d6f1646ad17.
        chapter_number (int): The number of the chapter
             Example: 1.
        description (str): A description of the chapter. HTML tags are stripped away from this field, use
            `html_description` field in case HTML tags are needed.
             Example: We kept on ascending, with occasional periods of quick descent, but in the main always ascending.
            Suddenly, I became conscious of the fact that the driver was in the act of pulling up the horses in the
            courtyard of a vast ruined castle, from whose tall black windows came no ray of light, and whose broken
            battlements showed a jagged line against the moonlit sky.
            .
        html_description (str): A description of the chapter. This field may contain HTML tags.
             Example: <p>We kept on ascending, with occasional periods of quick descent, but in the main always ascending.
            Suddenly, I became conscious of the fact that the driver was in the act of pulling up the horses in the
            courtyard of a vast ruined castle, from whose tall black windows came no ray of light, and whose broken
            battlements showed a jagged line against the moonlit sky.</p>
            .
        duration_ms (int): The chapter length in milliseconds.
             Example: 1686230.
        explicit (bool): Whether or not the chapter has explicit content (true = yes it does; false = no it does not OR
            unknown).
        external_urls (ExternalUrlObject):
        href (str): A link to the Web API endpoint providing full details of the chapter.
             Example: https://api.spotify.com/v1/episodes/5Xt5DXGzch68nYYamXrNxZ.
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the chapter.
             Example: 5Xt5DXGzch68nYYamXrNxZ.
        images (list['ImageObject']): The cover art for the chapter in various sizes, widest first.
        is_playable (bool): True if the chapter is playable in the given market. Otherwise false.
        languages (list[str]): A list of the languages used in the chapter, identified by their [ISO
            639-1](https://en.wikipedia.org/wiki/ISO_639) code.
             Example: ['fr', 'en'].
        name (str): The name of the chapter.
             Example: Starting Your Own Podcast: Tips, Tricks, and Advice From Anchor Creators
            .
        release_date (str): The date the chapter was first released, for example `"1981-12-15"`. Depending on the
            precision, it might be shown as `"1981"` or `"1981-12"`.
             Example: 1981-12-15.
        release_date_precision (ChapterBaseReleaseDatePrecision): The precision with which `release_date` value is
            known.
             Example: day.
        type_ (ChapterBaseType): The object type.
        uri (str): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the chapter.
             Example: spotify:episode:0zLhl3WsOCQHbe1BPTiHgr.
        available_markets (Union[Unset, list[str]]): A list of the countries in which the chapter can be played,
            identified by their [ISO 3166-1 alpha-2](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.
        resume_point (Union[Unset, ResumePointObject]):
        restrictions (Union[Unset, ChapterRestrictionObject]):
    """

    audio_preview_url: Union[None, str]
    chapter_number: int
    description: str
    html_description: str
    duration_ms: int
    explicit: bool
    external_urls: "ExternalUrlObject"
    href: str
    id: str
    images: list["ImageObject"]
    is_playable: bool
    languages: list[str]
    name: str
    release_date: str
    release_date_precision: ChapterBaseReleaseDatePrecision
    type_: ChapterBaseType
    uri: str
    available_markets: Union[Unset, list[str]] = UNSET
    resume_point: Union[Unset, "ResumePointObject"] = UNSET
    restrictions: Union[Unset, "ChapterRestrictionObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audio_preview_url: Union[None, str]
        audio_preview_url = self.audio_preview_url

        chapter_number = self.chapter_number

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

        is_playable = self.is_playable

        languages = self.languages

        name = self.name

        release_date = self.release_date

        release_date_precision = self.release_date_precision.value

        type_ = self.type_.value

        uri = self.uri

        available_markets: Union[Unset, list[str]] = UNSET
        if not isinstance(self.available_markets, Unset):
            available_markets = self.available_markets

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
                "chapter_number": chapter_number,
                "description": description,
                "html_description": html_description,
                "duration_ms": duration_ms,
                "explicit": explicit,
                "external_urls": external_urls,
                "href": href,
                "id": id,
                "images": images,
                "is_playable": is_playable,
                "languages": languages,
                "name": name,
                "release_date": release_date,
                "release_date_precision": release_date_precision,
                "type": type_,
                "uri": uri,
            }
        )
        if available_markets is not UNSET:
            field_dict["available_markets"] = available_markets
        if resume_point is not UNSET:
            field_dict["resume_point"] = resume_point
        if restrictions is not UNSET:
            field_dict["restrictions"] = restrictions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chapter_restriction_object import ChapterRestrictionObject
        from ..models.external_url_object import ExternalUrlObject
        from ..models.image_object import ImageObject
        from ..models.resume_point_object import ResumePointObject

        d = dict(src_dict)

        def _parse_audio_preview_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        audio_preview_url = _parse_audio_preview_url(d.pop("audio_preview_url"))

        chapter_number = d.pop("chapter_number")

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

        is_playable = d.pop("is_playable")

        languages = cast(list[str], d.pop("languages"))

        name = d.pop("name")

        release_date = d.pop("release_date")

        release_date_precision = ChapterBaseReleaseDatePrecision(d.pop("release_date_precision"))

        type_ = ChapterBaseType(d.pop("type"))

        uri = d.pop("uri")

        available_markets = cast(list[str], d.pop("available_markets", UNSET))

        _resume_point = d.pop("resume_point", UNSET)
        resume_point: Union[Unset, ResumePointObject]
        if isinstance(_resume_point, Unset):
            resume_point = UNSET
        else:
            resume_point = ResumePointObject.from_dict(_resume_point)

        _restrictions = d.pop("restrictions", UNSET)
        restrictions: Union[Unset, ChapterRestrictionObject]
        if isinstance(_restrictions, Unset):
            restrictions = UNSET
        else:
            restrictions = ChapterRestrictionObject.from_dict(_restrictions)

        simplified_chapter_object = cls(
            audio_preview_url=audio_preview_url,
            chapter_number=chapter_number,
            description=description,
            html_description=html_description,
            duration_ms=duration_ms,
            explicit=explicit,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            is_playable=is_playable,
            languages=languages,
            name=name,
            release_date=release_date,
            release_date_precision=release_date_precision,
            type_=type_,
            uri=uri,
            available_markets=available_markets,
            resume_point=resume_point,
            restrictions=restrictions,
        )

        simplified_chapter_object.additional_properties = d
        return simplified_chapter_object

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
