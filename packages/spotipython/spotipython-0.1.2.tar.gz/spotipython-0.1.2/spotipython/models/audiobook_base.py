from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.audiobook_base_type import AudiobookBaseType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.author_object import AuthorObject
    from ..models.copyright_object import CopyrightObject
    from ..models.external_url_object import ExternalUrlObject
    from ..models.image_object import ImageObject
    from ..models.narrator_object import NarratorObject


T = TypeVar("T", bound="AudiobookBase")


@_attrs_define
class AudiobookBase:
    """
    Attributes:
        authors (list['AuthorObject']): The author(s) for the audiobook.
        available_markets (list[str]): A list of the countries in which the audiobook can be played, identified by their
            [ISO 3166-1 alpha-2](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.
        copyrights (list['CopyrightObject']): The copyright statements of the audiobook.
        description (str): A description of the audiobook. HTML tags are stripped away from this field, use
            `html_description` field in case HTML tags are needed.
        html_description (str): A description of the audiobook. This field may contain HTML tags.
        explicit (bool): Whether or not the audiobook has explicit content (true = yes it does; false = no it does not
            OR unknown).
        external_urls (ExternalUrlObject):
        href (str): A link to the Web API endpoint providing full details of the audiobook.
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the audiobook.
        images (list['ImageObject']): The cover art for the audiobook in various sizes, widest first.
        languages (list[str]): A list of the languages used in the audiobook, identified by their [ISO
            639](https://en.wikipedia.org/wiki/ISO_639) code.
        media_type (str): The media type of the audiobook.
        name (str): The name of the audiobook.
        narrators (list['NarratorObject']): The narrator(s) for the audiobook.
        publisher (str): The publisher of the audiobook.
        type_ (AudiobookBaseType): The object type.
        uri (str): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the audiobook.
        total_chapters (int): The number of chapters in this audiobook.
        edition (Union[Unset, str]): The edition of the audiobook.
             Example: Unabridged.
    """

    authors: list["AuthorObject"]
    available_markets: list[str]
    copyrights: list["CopyrightObject"]
    description: str
    html_description: str
    explicit: bool
    external_urls: "ExternalUrlObject"
    href: str
    id: str
    images: list["ImageObject"]
    languages: list[str]
    media_type: str
    name: str
    narrators: list["NarratorObject"]
    publisher: str
    type_: AudiobookBaseType
    uri: str
    total_chapters: int
    edition: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authors = []
        for authors_item_data in self.authors:
            authors_item = authors_item_data.to_dict()
            authors.append(authors_item)

        available_markets = self.available_markets

        copyrights = []
        for copyrights_item_data in self.copyrights:
            copyrights_item = copyrights_item_data.to_dict()
            copyrights.append(copyrights_item)

        description = self.description

        html_description = self.html_description

        explicit = self.explicit

        external_urls = self.external_urls.to_dict()

        href = self.href

        id = self.id

        images = []
        for images_item_data in self.images:
            images_item = images_item_data.to_dict()
            images.append(images_item)

        languages = self.languages

        media_type = self.media_type

        name = self.name

        narrators = []
        for narrators_item_data in self.narrators:
            narrators_item = narrators_item_data.to_dict()
            narrators.append(narrators_item)

        publisher = self.publisher

        type_ = self.type_.value

        uri = self.uri

        total_chapters = self.total_chapters

        edition = self.edition

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authors": authors,
                "available_markets": available_markets,
                "copyrights": copyrights,
                "description": description,
                "html_description": html_description,
                "explicit": explicit,
                "external_urls": external_urls,
                "href": href,
                "id": id,
                "images": images,
                "languages": languages,
                "media_type": media_type,
                "name": name,
                "narrators": narrators,
                "publisher": publisher,
                "type": type_,
                "uri": uri,
                "total_chapters": total_chapters,
            }
        )
        if edition is not UNSET:
            field_dict["edition"] = edition

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.author_object import AuthorObject
        from ..models.copyright_object import CopyrightObject
        from ..models.external_url_object import ExternalUrlObject
        from ..models.image_object import ImageObject
        from ..models.narrator_object import NarratorObject

        d = dict(src_dict)
        authors = []
        _authors = d.pop("authors")
        for authors_item_data in _authors:
            authors_item = AuthorObject.from_dict(authors_item_data)

            authors.append(authors_item)

        available_markets = cast(list[str], d.pop("available_markets"))

        copyrights = []
        _copyrights = d.pop("copyrights")
        for copyrights_item_data in _copyrights:
            copyrights_item = CopyrightObject.from_dict(copyrights_item_data)

            copyrights.append(copyrights_item)

        description = d.pop("description")

        html_description = d.pop("html_description")

        explicit = d.pop("explicit")

        external_urls = ExternalUrlObject.from_dict(d.pop("external_urls"))

        href = d.pop("href")

        id = d.pop("id")

        images = []
        _images = d.pop("images")
        for images_item_data in _images:
            images_item = ImageObject.from_dict(images_item_data)

            images.append(images_item)

        languages = cast(list[str], d.pop("languages"))

        media_type = d.pop("media_type")

        name = d.pop("name")

        narrators = []
        _narrators = d.pop("narrators")
        for narrators_item_data in _narrators:
            narrators_item = NarratorObject.from_dict(narrators_item_data)

            narrators.append(narrators_item)

        publisher = d.pop("publisher")

        type_ = AudiobookBaseType(d.pop("type"))

        uri = d.pop("uri")

        total_chapters = d.pop("total_chapters")

        edition = d.pop("edition", UNSET)

        audiobook_base = cls(
            authors=authors,
            available_markets=available_markets,
            copyrights=copyrights,
            description=description,
            html_description=html_description,
            explicit=explicit,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            languages=languages,
            media_type=media_type,
            name=name,
            narrators=narrators,
            publisher=publisher,
            type_=type_,
            uri=uri,
            total_chapters=total_chapters,
            edition=edition,
        )

        audiobook_base.additional_properties = d
        return audiobook_base

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
