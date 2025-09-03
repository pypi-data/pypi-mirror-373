from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.artist_object_type import ArtistObjectType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_url_object import ExternalUrlObject
    from ..models.followers_object import FollowersObject
    from ..models.image_object import ImageObject


T = TypeVar("T", bound="ArtistObject")


@_attrs_define
class ArtistObject:
    """
    Attributes:
        external_urls (Union[Unset, ExternalUrlObject]):
        followers (Union[Unset, FollowersObject]):
        genres (Union[Unset, list[str]]): A list of the genres the artist is associated with. If not yet classified, the
            array is empty.
             Example: ['Prog rock', 'Grunge'].
        href (Union[Unset, str]): A link to the Web API endpoint providing full details of the artist.
        id (Union[Unset, str]): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the artist.
        images (Union[Unset, list['ImageObject']]): Images of the artist in various sizes, widest first.
        name (Union[Unset, str]): The name of the artist.
        popularity (Union[Unset, int]): The popularity of the artist. The value will be between 0 and 100, with 100
            being the most popular. The artist's popularity is calculated from the popularity of all the artist's tracks.
        type_ (Union[Unset, ArtistObjectType]): The object type.
        uri (Union[Unset, str]): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the artist.
    """

    external_urls: Union[Unset, "ExternalUrlObject"] = UNSET
    followers: Union[Unset, "FollowersObject"] = UNSET
    genres: Union[Unset, list[str]] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    images: Union[Unset, list["ImageObject"]] = UNSET
    name: Union[Unset, str] = UNSET
    popularity: Union[Unset, int] = UNSET
    type_: Union[Unset, ArtistObjectType] = UNSET
    uri: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        external_urls: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.external_urls, Unset):
            external_urls = self.external_urls.to_dict()

        followers: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.followers, Unset):
            followers = self.followers.to_dict()

        genres: Union[Unset, list[str]] = UNSET
        if not isinstance(self.genres, Unset):
            genres = self.genres

        href = self.href

        id = self.id

        images: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.images, Unset):
            images = []
            for images_item_data in self.images:
                images_item = images_item_data.to_dict()
                images.append(images_item)

        name = self.name

        popularity = self.popularity

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_urls is not UNSET:
            field_dict["external_urls"] = external_urls
        if followers is not UNSET:
            field_dict["followers"] = followers
        if genres is not UNSET:
            field_dict["genres"] = genres
        if href is not UNSET:
            field_dict["href"] = href
        if id is not UNSET:
            field_dict["id"] = id
        if images is not UNSET:
            field_dict["images"] = images
        if name is not UNSET:
            field_dict["name"] = name
        if popularity is not UNSET:
            field_dict["popularity"] = popularity
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_url_object import ExternalUrlObject
        from ..models.followers_object import FollowersObject
        from ..models.image_object import ImageObject

        d = dict(src_dict)
        _external_urls = d.pop("external_urls", UNSET)
        external_urls: Union[Unset, ExternalUrlObject]
        if isinstance(_external_urls, Unset):
            external_urls = UNSET
        else:
            external_urls = ExternalUrlObject.from_dict(_external_urls)

        _followers = d.pop("followers", UNSET)
        followers: Union[Unset, FollowersObject]
        if isinstance(_followers, Unset):
            followers = UNSET
        else:
            followers = FollowersObject.from_dict(_followers)

        genres = cast(list[str], d.pop("genres", UNSET))

        href = d.pop("href", UNSET)

        id = d.pop("id", UNSET)

        images = []
        _images = d.pop("images", UNSET)
        for images_item_data in _images or []:
            images_item = ImageObject.from_dict(images_item_data)

            images.append(images_item)

        name = d.pop("name", UNSET)

        popularity = d.pop("popularity", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, ArtistObjectType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = ArtistObjectType(_type_)

        uri = d.pop("uri", UNSET)

        artist_object = cls(
            external_urls=external_urls,
            followers=followers,
            genres=genres,
            href=href,
            id=id,
            images=images,
            name=name,
            popularity=popularity,
            type_=type_,
            uri=uri,
        )

        artist_object.additional_properties = d
        return artist_object

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
