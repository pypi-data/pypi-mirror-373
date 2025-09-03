from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.playlist_user_object_type import PlaylistUserObjectType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_url_object import ExternalUrlObject


T = TypeVar("T", bound="PlaylistUserObject")


@_attrs_define
class PlaylistUserObject:
    """
    Attributes:
        external_urls (Union[Unset, ExternalUrlObject]):
        href (Union[Unset, str]): A link to the Web API endpoint for this user.
        id (Union[Unset, str]): The [Spotify user ID](/documentation/web-api/concepts/spotify-uris-ids) for this user.
        type_ (Union[Unset, PlaylistUserObjectType]): The object type.
        uri (Union[Unset, str]): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for this user.
    """

    external_urls: Union[Unset, "ExternalUrlObject"] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type_: Union[Unset, PlaylistUserObjectType] = UNSET
    uri: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        external_urls: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.external_urls, Unset):
            external_urls = self.external_urls.to_dict()

        href = self.href

        id = self.id

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_urls is not UNSET:
            field_dict["external_urls"] = external_urls
        if href is not UNSET:
            field_dict["href"] = href
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_url_object import ExternalUrlObject

        d = dict(src_dict)
        _external_urls = d.pop("external_urls", UNSET)
        external_urls: Union[Unset, ExternalUrlObject]
        if isinstance(_external_urls, Unset):
            external_urls = UNSET
        else:
            external_urls = ExternalUrlObject.from_dict(_external_urls)

        href = d.pop("href", UNSET)

        id = d.pop("id", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, PlaylistUserObjectType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = PlaylistUserObjectType(_type_)

        uri = d.pop("uri", UNSET)

        playlist_user_object = cls(
            external_urls=external_urls,
            href=href,
            id=id,
            type_=type_,
            uri=uri,
        )

        playlist_user_object.additional_properties = d
        return playlist_user_object

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
