from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.album_base_album_type import AlbumBaseAlbumType
from ..models.album_base_release_date_precision import AlbumBaseReleaseDatePrecision
from ..models.album_base_type import AlbumBaseType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.album_restriction_object import AlbumRestrictionObject
    from ..models.copyright_object import CopyrightObject
    from ..models.external_id_object import ExternalIdObject
    from ..models.external_url_object import ExternalUrlObject
    from ..models.image_object import ImageObject
    from ..models.paging_simplified_track_object import PagingSimplifiedTrackObject
    from ..models.simplified_artist_object import SimplifiedArtistObject


T = TypeVar("T", bound="AlbumObject")


@_attrs_define
class AlbumObject:
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
        tracks (PagingSimplifiedTrackObject):
        copyrights (list['CopyrightObject']): The copyright statements of the album.
        external_ids (ExternalIdObject):
        genres (list[str]): **Deprecated** The array is always empty.
        label (str): The label associated with the album.
        popularity (int): The popularity of the album. The value will be between 0 and 100, with 100 being the most
            popular.
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
    tracks: "PagingSimplifiedTrackObject"
    copyrights: list["CopyrightObject"]
    external_ids: "ExternalIdObject"
    genres: list[str]
    label: str
    popularity: int
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

        tracks = self.tracks.to_dict()

        copyrights = []
        for copyrights_item_data in self.copyrights:
            copyrights_item = copyrights_item_data.to_dict()
            copyrights.append(copyrights_item)

        external_ids = self.external_ids.to_dict()

        genres = self.genres

        label = self.label

        popularity = self.popularity

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
                "tracks": tracks,
                "copyrights": copyrights,
                "external_ids": external_ids,
                "genres": genres,
                "label": label,
                "popularity": popularity,
            }
        )
        if restrictions is not UNSET:
            field_dict["restrictions"] = restrictions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.album_restriction_object import AlbumRestrictionObject
        from ..models.copyright_object import CopyrightObject
        from ..models.external_id_object import ExternalIdObject
        from ..models.external_url_object import ExternalUrlObject
        from ..models.image_object import ImageObject
        from ..models.paging_simplified_track_object import PagingSimplifiedTrackObject
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

        tracks = PagingSimplifiedTrackObject.from_dict(d.pop("tracks"))

        copyrights = []
        _copyrights = d.pop("copyrights")
        for copyrights_item_data in _copyrights:
            copyrights_item = CopyrightObject.from_dict(copyrights_item_data)

            copyrights.append(copyrights_item)

        external_ids = ExternalIdObject.from_dict(d.pop("external_ids"))

        genres = cast(list[str], d.pop("genres"))

        label = d.pop("label")

        popularity = d.pop("popularity")

        _restrictions = d.pop("restrictions", UNSET)
        restrictions: Union[Unset, AlbumRestrictionObject]
        if isinstance(_restrictions, Unset):
            restrictions = UNSET
        else:
            restrictions = AlbumRestrictionObject.from_dict(_restrictions)

        album_object = cls(
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
            tracks=tracks,
            copyrights=copyrights,
            external_ids=external_ids,
            genres=genres,
            label=label,
            popularity=popularity,
            restrictions=restrictions,
        )

        album_object.additional_properties = d
        return album_object

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
