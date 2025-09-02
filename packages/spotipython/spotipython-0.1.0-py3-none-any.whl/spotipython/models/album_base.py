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


T = TypeVar("T", bound="AlbumBase")


@_attrs_define
class AlbumBase:
    """
    Attributes:
        album_type (AlbumBaseAlbumType): The type of the album.
             Example: compilation.
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
        total_tracks (int): The number of tracks in the album. Example: 9.
        type_ (AlbumBaseType): The object type.
        uri (str): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the album.
             Example: spotify:album:2up3OPMp9Tb4dAKM2erWXQ.
        copyrights (Union[Unset, list['CopyrightObject']]): The copyright statements of the album.
        external_ids (Union[Unset, ExternalIdObject]):
        genres (Union[Unset, list[str]]): A list of the genres the album is associated with. If not yet classified, the
            array is empty.
             Example: ['Egg punk', 'Noise rock'].
        label (Union[Unset, str]): The label associated with the album.
        popularity (Union[Unset, int]): The popularity of the album. The value will be between 0 and 100, with 100 being
            the most popular.
        restrictions (Union[Unset, AlbumRestrictionObject]):
    """

    album_type: AlbumBaseAlbumType
    available_markets: list[str]
    external_urls: "ExternalUrlObject"
    href: str
    id: str
    images: list["ImageObject"]
    name: str
    release_date: str
    release_date_precision: AlbumBaseReleaseDatePrecision
    total_tracks: int
    type_: AlbumBaseType
    uri: str
    copyrights: Union[Unset, list["CopyrightObject"]] = UNSET
    external_ids: Union[Unset, "ExternalIdObject"] = UNSET
    genres: Union[Unset, list[str]] = UNSET
    label: Union[Unset, str] = UNSET
    popularity: Union[Unset, int] = UNSET
    restrictions: Union[Unset, "AlbumRestrictionObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        album_type = self.album_type.value

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

        total_tracks = self.total_tracks

        type_ = self.type_.value

        uri = self.uri

        copyrights: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.copyrights, Unset):
            copyrights = []
            for copyrights_item_data in self.copyrights:
                copyrights_item = copyrights_item_data.to_dict()
                copyrights.append(copyrights_item)

        external_ids: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.external_ids, Unset):
            external_ids = self.external_ids.to_dict()

        genres: Union[Unset, list[str]] = UNSET
        if not isinstance(self.genres, Unset):
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
                "available_markets": available_markets,
                "external_urls": external_urls,
                "href": href,
                "id": id,
                "images": images,
                "name": name,
                "release_date": release_date,
                "release_date_precision": release_date_precision,
                "total_tracks": total_tracks,
                "type": type_,
                "uri": uri,
            }
        )
        if copyrights is not UNSET:
            field_dict["copyrights"] = copyrights
        if external_ids is not UNSET:
            field_dict["external_ids"] = external_ids
        if genres is not UNSET:
            field_dict["genres"] = genres
        if label is not UNSET:
            field_dict["label"] = label
        if popularity is not UNSET:
            field_dict["popularity"] = popularity
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

        d = dict(src_dict)
        album_type = AlbumBaseAlbumType(d.pop("album_type"))

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

        total_tracks = d.pop("total_tracks")

        type_ = AlbumBaseType(d.pop("type"))

        uri = d.pop("uri")

        copyrights = []
        _copyrights = d.pop("copyrights", UNSET)
        for copyrights_item_data in _copyrights or []:
            copyrights_item = CopyrightObject.from_dict(copyrights_item_data)

            copyrights.append(copyrights_item)

        _external_ids = d.pop("external_ids", UNSET)
        external_ids: Union[Unset, ExternalIdObject]
        if isinstance(_external_ids, Unset):
            external_ids = UNSET
        else:
            external_ids = ExternalIdObject.from_dict(_external_ids)

        genres = cast(list[str], d.pop("genres", UNSET))

        label = d.pop("label", UNSET)

        popularity = d.pop("popularity", UNSET)

        _restrictions = d.pop("restrictions", UNSET)
        restrictions: Union[Unset, AlbumRestrictionObject]
        if isinstance(_restrictions, Unset):
            restrictions = UNSET
        else:
            restrictions = AlbumRestrictionObject.from_dict(_restrictions)

        album_base = cls(
            album_type=album_type,
            available_markets=available_markets,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            name=name,
            release_date=release_date,
            release_date_precision=release_date_precision,
            total_tracks=total_tracks,
            type_=type_,
            uri=uri,
            copyrights=copyrights,
            external_ids=external_ids,
            genres=genres,
            label=label,
            popularity=popularity,
            restrictions=restrictions,
        )

        album_base.additional_properties = d
        return album_base

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
