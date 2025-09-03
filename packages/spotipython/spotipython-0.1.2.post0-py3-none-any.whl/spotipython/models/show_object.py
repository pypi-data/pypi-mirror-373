from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.show_base_type import ShowBaseType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.copyright_object import CopyrightObject
    from ..models.external_url_object import ExternalUrlObject
    from ..models.image_object import ImageObject
    from ..models.paging_simplified_episode_object import PagingSimplifiedEpisodeObject


T = TypeVar("T", bound="ShowObject")


@_attrs_define
class ShowObject:
    """
    Attributes:
        copyrights (list['CopyrightObject']): The copyright statements of the show.
        description (str): A description of the show. HTML tags are stripped away from this field, use
            `html_description` field in case HTML tags are needed.
        html_description (str): A description of the show. This field may contain HTML tags.
        explicit (bool): Whether or not the show has explicit content (true = yes it does; false = no it does not OR
            unknown).
        external_urls (ExternalUrlObject):
        href (str): A link to the Web API endpoint providing full details of the show.
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the show.
        images (list['ImageObject']): The cover art for the show in various sizes, widest first.
        is_externally_hosted (bool): True if all of the shows episodes are hosted outside of Spotify's CDN. This field
            might be `null` in some cases.
        languages (list[str]): A list of the languages used in the show, identified by their [ISO
            639](https://en.wikipedia.org/wiki/ISO_639) code.
        media_type (str): The media type of the show.
        name (str): The name of the episode.
        publisher (str): The publisher of the show.
        type_ (ShowBaseType): The object type.
        uri (str): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the show.
        total_episodes (int): The total number of episodes in the show.
        episodes (PagingSimplifiedEpisodeObject):
        available_markets (Union[Unset, list[str]]): A list of the countries in which the show can be played, identified
            by their [ISO 3166-1 alpha-2](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.
    """

    copyrights: list["CopyrightObject"]
    description: str
    html_description: str
    explicit: bool
    external_urls: "ExternalUrlObject"
    href: str
    id: str
    images: list["ImageObject"]
    is_externally_hosted: bool
    languages: list[str]
    media_type: str
    name: str
    publisher: str
    type_: ShowBaseType
    uri: str
    total_episodes: int
    episodes: "PagingSimplifiedEpisodeObject"
    available_markets: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

        is_externally_hosted = self.is_externally_hosted

        languages = self.languages

        media_type = self.media_type

        name = self.name

        publisher = self.publisher

        type_ = self.type_.value

        uri = self.uri

        total_episodes = self.total_episodes

        episodes = self.episodes.to_dict()

        available_markets: Union[Unset, list[str]] = UNSET
        if not isinstance(self.available_markets, Unset):
            available_markets = self.available_markets

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "copyrights": copyrights,
                "description": description,
                "html_description": html_description,
                "explicit": explicit,
                "external_urls": external_urls,
                "href": href,
                "id": id,
                "images": images,
                "is_externally_hosted": is_externally_hosted,
                "languages": languages,
                "media_type": media_type,
                "name": name,
                "publisher": publisher,
                "type": type_,
                "uri": uri,
                "total_episodes": total_episodes,
                "episodes": episodes,
            }
        )
        if available_markets is not UNSET:
            field_dict["available_markets"] = available_markets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.copyright_object import CopyrightObject
        from ..models.external_url_object import ExternalUrlObject
        from ..models.image_object import ImageObject
        from ..models.paging_simplified_episode_object import PagingSimplifiedEpisodeObject

        d = dict(src_dict)
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

        is_externally_hosted = d.pop("is_externally_hosted")

        languages = cast(list[str], d.pop("languages"))

        media_type = d.pop("media_type")

        name = d.pop("name")

        publisher = d.pop("publisher")

        type_ = ShowBaseType(d.pop("type"))

        uri = d.pop("uri")

        total_episodes = d.pop("total_episodes")

        episodes = PagingSimplifiedEpisodeObject.from_dict(d.pop("episodes"))

        available_markets = cast(list[str], d.pop("available_markets", UNSET))

        show_object = cls(
            copyrights=copyrights,
            description=description,
            html_description=html_description,
            explicit=explicit,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            is_externally_hosted=is_externally_hosted,
            languages=languages,
            media_type=media_type,
            name=name,
            publisher=publisher,
            type_=type_,
            uri=uri,
            total_episodes=total_episodes,
            episodes=episodes,
            available_markets=available_markets,
        )

        show_object.additional_properties = d
        return show_object

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
