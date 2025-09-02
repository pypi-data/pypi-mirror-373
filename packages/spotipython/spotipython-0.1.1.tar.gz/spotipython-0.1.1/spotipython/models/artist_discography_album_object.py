from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.album_base_album_type import AlbumBaseAlbumType
from ..models.album_base_release_date_precision import AlbumBaseReleaseDatePrecision
from ..models.album_base_type import AlbumBaseType
from ..models.artist_discography_album_object_album_group import ArtistDiscographyAlbumObjectAlbumGroup
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.album_restriction_object import AlbumRestrictionObject
    from ..models.external_url_object import ExternalUrlObject
    from ..models.image_object import ImageObject
    from ..models.simplified_artist_object import SimplifiedArtistObject


T = TypeVar("T", bound="ArtistDiscographyAlbumObject")


@_attrs_define
class ArtistDiscographyAlbumObject:
    """
    Attributes:
        album_type (AlbumBaseAlbumType): The type of the album.
             Example: compilation.
        total_tracks (int): The number of tracks in the album. Example: 9.
        available_markets (list[str]): The markets in which the album is available: [ISO 3166-1 alpha-2 country
            codes](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). _**NOTE**: an album is considered available in a market
            when at least 1 of its tracks is available in that market._
             Example: ['CA', 'BR', 'IT'].
        external_urls (ExternalUrlObject):
        href (str): A link to the Web API endpoint providing full details of the album.
        id (str): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the album.
             Example: 2up3OPMp9Tb4dAKM2erWXQ.
        images (list['ImageObject']): The cover art for the album in various sizes, widest first.
        name (str): The name of the album. In case of an album takedown, the value may be an empty string.
        release_date (str): The date the album was first released.
             Example: 1981-12.
        release_date_precision (AlbumBaseReleaseDatePrecision): The precision with which `release_date` value is known.
             Example: year.
        type_ (AlbumBaseType): The object type.
        uri (str): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the album.
             Example: spotify:album:2up3OPMp9Tb4dAKM2erWXQ.
        artists (list['SimplifiedArtistObject']): The artists of the album. Each artist object includes a link in `href`
            to more detailed information about the artist.
        album_group (ArtistDiscographyAlbumObjectAlbumGroup): This field describes the relationship between the artist
            and the album.
             Example: compilation.
        restrictions (Union[Unset, AlbumRestrictionObject]):
    """

    album_type: AlbumBaseAlbumType
    total_tracks: int
    available_markets: list[str]
    external_urls: "ExternalUrlObject"
    href: str
    id: str
    images: list["ImageObject"]
    name: str
    release_date: str
    release_date_precision: AlbumBaseReleaseDatePrecision
    type_: AlbumBaseType
    uri: str
    artists: list["SimplifiedArtistObject"]
    album_group: ArtistDiscographyAlbumObjectAlbumGroup
    restrictions: Union[Unset, "AlbumRestrictionObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        album_type = self.album_type.value

        total_tracks = self.total_tracks

        available_markets = self.available_markets

        external_urls = self.external_urls.to_dict()

        href = self.href

        id = self.id

        images = []
        for images_item_data in self.images:
            images_item = images_item_data.to_dict()
            images.append(images_item)

        name = self.name

        release_date = self.release_date

        release_date_precision = self.release_date_precision.value

        type_ = self.type_.value

        uri = self.uri

        artists = []
        for artists_item_data in self.artists:
            artists_item = artists_item_data.to_dict()
            artists.append(artists_item)

        album_group = self.album_group.value

        restrictions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.restrictions, Unset):
            restrictions = self.restrictions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "album_type": album_type,
                "total_tracks": total_tracks,
                "available_markets": available_markets,
                "external_urls": external_urls,
                "href": href,
                "id": id,
                "images": images,
                "name": name,
                "release_date": release_date,
                "release_date_precision": release_date_precision,
                "type": type_,
                "uri": uri,
                "artists": artists,
                "album_group": album_group,
            }
        )
        if restrictions is not UNSET:
            field_dict["restrictions"] = restrictions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.album_restriction_object import AlbumRestrictionObject
        from ..models.external_url_object import ExternalUrlObject
        from ..models.image_object import ImageObject
        from ..models.simplified_artist_object import SimplifiedArtistObject

        d = dict(src_dict)
        album_type = AlbumBaseAlbumType(d.pop("album_type"))

        total_tracks = d.pop("total_tracks")

        available_markets = cast(list[str], d.pop("available_markets"))

        external_urls = ExternalUrlObject.from_dict(d.pop("external_urls"))

        href = d.pop("href")

        id = d.pop("id")

        images = []
        _images = d.pop("images")
        for images_item_data in _images:
            images_item = ImageObject.from_dict(images_item_data)

            images.append(images_item)

        name = d.pop("name")

        release_date = d.pop("release_date")

        release_date_precision = AlbumBaseReleaseDatePrecision(d.pop("release_date_precision"))

        type_ = AlbumBaseType(d.pop("type"))

        uri = d.pop("uri")

        artists = []
        _artists = d.pop("artists")
        for artists_item_data in _artists:
            artists_item = SimplifiedArtistObject.from_dict(artists_item_data)

            artists.append(artists_item)

        album_group = ArtistDiscographyAlbumObjectAlbumGroup(d.pop("album_group"))

        _restrictions = d.pop("restrictions", UNSET)
        restrictions: Union[Unset, AlbumRestrictionObject]
        if isinstance(_restrictions, Unset):
            restrictions = UNSET
        else:
            restrictions = AlbumRestrictionObject.from_dict(_restrictions)

        artist_discography_album_object = cls(
            album_type=album_type,
            total_tracks=total_tracks,
            available_markets=available_markets,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            name=name,
            release_date=release_date,
            release_date_precision=release_date_precision,
            type_=type_,
            uri=uri,
            artists=artists,
            album_group=album_group,
            restrictions=restrictions,
        )

        artist_discography_album_object.additional_properties = d
        return artist_discography_album_object

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
