from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.paging_simplified_album_object import PagingSimplifiedAlbumObject


T = TypeVar("T", bound="GetNewReleasesResponse200")


@_attrs_define
class GetNewReleasesResponse200:
    """
    Attributes:
        albums (PagingSimplifiedAlbumObject):
    """

    albums: "PagingSimplifiedAlbumObject"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        albums = self.albums.to_dict()

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
        from ..models.paging_simplified_album_object import PagingSimplifiedAlbumObject

        d = dict(src_dict)
        albums = PagingSimplifiedAlbumObject.from_dict(d.pop("albums"))

        get_new_releases_response_200 = cls(
            albums=albums,
        )

        get_new_releases_response_200.additional_properties = d
        return get_new_releases_response_200

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
