from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.album_object import AlbumObject


T = TypeVar("T", bound="GetMultipleAlbumsResponse200")


@_attrs_define
class GetMultipleAlbumsResponse200:
    """
    Attributes:
        albums (list['AlbumObject']):
    """

    albums: list["AlbumObject"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        albums = []
        for albums_item_data in self.albums:
            albums_item = albums_item_data.to_dict()
            albums.append(albums_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "albums": albums,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.album_object import AlbumObject

        d = dict(src_dict)
        albums = []
        _albums = d.pop("albums")
        for albums_item_data in _albums:
            albums_item = AlbumObject.from_dict(albums_item_data)

            albums.append(albums_item)

        get_multiple_albums_response_200 = cls(
            albums=albums,
        )

        get_multiple_albums_response_200.additional_properties = d
        return get_multiple_albums_response_200

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
