from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.artist_object import ArtistObject


T = TypeVar("T", bound="GetAnArtistsRelatedArtistsResponse200")


@_attrs_define
class GetAnArtistsRelatedArtistsResponse200:
    """
    Attributes:
        artists (list['ArtistObject']):
    """

    artists: list["ArtistObject"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        artists = []
        for artists_item_data in self.artists:
            artists_item = artists_item_data.to_dict()
            artists.append(artists_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "artists": artists,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artist_object import ArtistObject

        d = dict(src_dict)
        artists = []
        _artists = d.pop("artists")
        for artists_item_data in _artists:
            artists_item = ArtistObject.from_dict(artists_item_data)

            artists.append(artists_item)

        get_an_artists_related_artists_response_200 = cls(
            artists=artists,
        )

        get_an_artists_related_artists_response_200.additional_properties = d
        return get_an_artists_related_artists_response_200

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
