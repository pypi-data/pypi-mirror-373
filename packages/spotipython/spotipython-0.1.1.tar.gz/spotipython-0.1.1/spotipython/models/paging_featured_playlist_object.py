from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.paging_playlist_object import PagingPlaylistObject


T = TypeVar("T", bound="PagingFeaturedPlaylistObject")


@_attrs_define
class PagingFeaturedPlaylistObject:
    """
    Attributes:
        message (Union[Unset, str]): The localized message of a playlist.
             Example: Popular Playlists.
        playlists (Union[Unset, PagingPlaylistObject]):
    """

    message: Union[Unset, str] = UNSET
    playlists: Union[Unset, "PagingPlaylistObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        playlists: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.playlists, Unset):
            playlists = self.playlists.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message
        if playlists is not UNSET:
            field_dict["playlists"] = playlists

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.paging_playlist_object import PagingPlaylistObject

        d = dict(src_dict)
        message = d.pop("message", UNSET)

        _playlists = d.pop("playlists", UNSET)
        playlists: Union[Unset, PagingPlaylistObject]
        if isinstance(_playlists, Unset):
            playlists = UNSET
        else:
            playlists = PagingPlaylistObject.from_dict(_playlists)

        paging_featured_playlist_object = cls(
            message=message,
            playlists=playlists,
        )

        paging_featured_playlist_object.additional_properties = d
        return paging_featured_playlist_object

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
