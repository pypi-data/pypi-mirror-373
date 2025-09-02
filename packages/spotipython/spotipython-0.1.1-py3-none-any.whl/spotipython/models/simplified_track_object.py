from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_url_object import ExternalUrlObject
    from ..models.linked_track_object import LinkedTrackObject
    from ..models.simplified_artist_object import SimplifiedArtistObject
    from ..models.track_restriction_object import TrackRestrictionObject


T = TypeVar("T", bound="SimplifiedTrackObject")


@_attrs_define
class SimplifiedTrackObject:
    """
    Attributes:
        artists (Union[Unset, list['SimplifiedArtistObject']]): The artists who performed the track. Each artist object
            includes a link in `href` to more detailed information about the artist.
        available_markets (Union[Unset, list[str]]): A list of the countries in which the track can be played,
            identified by their [ISO 3166-1 alpha-2](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.
        disc_number (Union[Unset, int]): The disc number (usually `1` unless the album consists of more than one disc).
        duration_ms (Union[Unset, int]): The track length in milliseconds.
        explicit (Union[Unset, bool]): Whether or not the track has explicit lyrics ( `true` = yes it does; `false` = no
            it does not OR unknown).
        external_urls (Union[Unset, ExternalUrlObject]):
        href (Union[Unset, str]): A link to the Web API endpoint providing full details of the track.
        id (Union[Unset, str]): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the track.
        is_playable (Union[Unset, bool]): Part of the response when [Track Relinking](/documentation/web-
            api/concepts/track-relinking/) is applied. If `true`, the track is playable in the given market. Otherwise
            `false`.
        linked_from (Union[Unset, LinkedTrackObject]):
        restrictions (Union[Unset, TrackRestrictionObject]):
        name (Union[Unset, str]): The name of the track.
        preview_url (Union[None, Unset, str]): A URL to a 30 second preview (MP3 format) of the track.
        track_number (Union[Unset, int]): The number of the track. If an album has several discs, the track number is
            the number on the specified disc.
        type_ (Union[Unset, str]): The object type: "track".
        uri (Union[Unset, str]): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the track.
        is_local (Union[Unset, bool]): Whether or not the track is from a local file.
    """

    artists: Union[Unset, list["SimplifiedArtistObject"]] = UNSET
    available_markets: Union[Unset, list[str]] = UNSET
    disc_number: Union[Unset, int] = UNSET
    duration_ms: Union[Unset, int] = UNSET
    explicit: Union[Unset, bool] = UNSET
    external_urls: Union[Unset, "ExternalUrlObject"] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    is_playable: Union[Unset, bool] = UNSET
    linked_from: Union[Unset, "LinkedTrackObject"] = UNSET
    restrictions: Union[Unset, "TrackRestrictionObject"] = UNSET
    name: Union[Unset, str] = UNSET
    preview_url: Union[None, Unset, str] = UNSET
    track_number: Union[Unset, int] = UNSET
    type_: Union[Unset, str] = UNSET
    uri: Union[Unset, str] = UNSET
    is_local: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        artists: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.artists, Unset):
            artists = []
            for artists_item_data in self.artists:
                artists_item = artists_item_data.to_dict()
                artists.append(artists_item)

        available_markets: Union[Unset, list[str]] = UNSET
        if not isinstance(self.available_markets, Unset):
            available_markets = self.available_markets

        disc_number = self.disc_number

        duration_ms = self.duration_ms

        explicit = self.explicit

        external_urls: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.external_urls, Unset):
            external_urls = self.external_urls.to_dict()

        href = self.href

        id = self.id

        is_playable = self.is_playable

        linked_from: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.linked_from, Unset):
            linked_from = self.linked_from.to_dict()

        restrictions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.restrictions, Unset):
            restrictions = self.restrictions.to_dict()

        name = self.name

        preview_url: Union[None, Unset, str]
        if isinstance(self.preview_url, Unset):
            preview_url = UNSET
        else:
            preview_url = self.preview_url

        track_number = self.track_number

        type_ = self.type_

        uri = self.uri

        is_local = self.is_local

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if artists is not UNSET:
            field_dict["artists"] = artists
        if available_markets is not UNSET:
            field_dict["available_markets"] = available_markets
        if disc_number is not UNSET:
            field_dict["disc_number"] = disc_number
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if explicit is not UNSET:
            field_dict["explicit"] = explicit
        if external_urls is not UNSET:
            field_dict["external_urls"] = external_urls
        if href is not UNSET:
            field_dict["href"] = href
        if id is not UNSET:
            field_dict["id"] = id
        if is_playable is not UNSET:
            field_dict["is_playable"] = is_playable
        if linked_from is not UNSET:
            field_dict["linked_from"] = linked_from
        if restrictions is not UNSET:
            field_dict["restrictions"] = restrictions
        if name is not UNSET:
            field_dict["name"] = name
        if preview_url is not UNSET:
            field_dict["preview_url"] = preview_url
        if track_number is not UNSET:
            field_dict["track_number"] = track_number
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uri is not UNSET:
            field_dict["uri"] = uri
        if is_local is not UNSET:
            field_dict["is_local"] = is_local

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_url_object import ExternalUrlObject
        from ..models.linked_track_object import LinkedTrackObject
        from ..models.simplified_artist_object import SimplifiedArtistObject
        from ..models.track_restriction_object import TrackRestrictionObject

        d = dict(src_dict)
        artists = []
        _artists = d.pop("artists", UNSET)
        for artists_item_data in _artists or []:
            artists_item = SimplifiedArtistObject.from_dict(artists_item_data)

            artists.append(artists_item)

        available_markets = cast(list[str], d.pop("available_markets", UNSET))

        disc_number = d.pop("disc_number", UNSET)

        duration_ms = d.pop("duration_ms", UNSET)

        explicit = d.pop("explicit", UNSET)

        _external_urls = d.pop("external_urls", UNSET)
        external_urls: Union[Unset, ExternalUrlObject]
        if isinstance(_external_urls, Unset):
            external_urls = UNSET
        else:
            external_urls = ExternalUrlObject.from_dict(_external_urls)

        href = d.pop("href", UNSET)

        id = d.pop("id", UNSET)

        is_playable = d.pop("is_playable", UNSET)

        _linked_from = d.pop("linked_from", UNSET)
        linked_from: Union[Unset, LinkedTrackObject]
        if isinstance(_linked_from, Unset):
            linked_from = UNSET
        else:
            linked_from = LinkedTrackObject.from_dict(_linked_from)

        _restrictions = d.pop("restrictions", UNSET)
        restrictions: Union[Unset, TrackRestrictionObject]
        if isinstance(_restrictions, Unset):
            restrictions = UNSET
        else:
            restrictions = TrackRestrictionObject.from_dict(_restrictions)

        name = d.pop("name", UNSET)

        def _parse_preview_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        preview_url = _parse_preview_url(d.pop("preview_url", UNSET))

        track_number = d.pop("track_number", UNSET)

        type_ = d.pop("type", UNSET)

        uri = d.pop("uri", UNSET)

        is_local = d.pop("is_local", UNSET)

        simplified_track_object = cls(
            artists=artists,
            available_markets=available_markets,
            disc_number=disc_number,
            duration_ms=duration_ms,
            explicit=explicit,
            external_urls=external_urls,
            href=href,
            id=id,
            is_playable=is_playable,
            linked_from=linked_from,
            restrictions=restrictions,
            name=name,
            preview_url=preview_url,
            track_number=track_number,
            type_=type_,
            uri=uri,
            is_local=is_local,
        )

        simplified_track_object.additional_properties = d
        return simplified_track_object

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
